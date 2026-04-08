"""
小红书糖尿病雷达数据抓取脚本
用于 GitHub Actions 自动化更新 radar-data.json

使用方法:
  python scripts/scrape_xhs.py

依赖: pip install httpx lxml beautifulsoup4
"""
import json, time, random, os, sys
from datetime import datetime
from pathlib import Path

try:
    import httpx
except ImportError:
    print('[ERROR] httpx not installed. Run: pip install httpx lxml')
    sys.exit(1)

# ─── 配置 ─────────────────────────────────────────
KEYWORDS = [
    '1型糖尿病', '2型糖尿病', '胰岛素泵',
    '糖尿病饮食', '血糖管理', '控糖',
    '糖尿病早餐', '糖尿病食谱', '动态血糖仪',
]
MAX_PER_KEYWORD = 30       # 每个关键词最多抓多少条
MIN_ENGAGE = 500           # 最低互动量（过滤垃圾内容）
REQUEST_DELAY = 1.5        # 请求间隔（秒），防止被封

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://www.xiaohongshu.com/',
    'Origin': 'https://www.xiaohongshu.com',
}

# ─── 工具函数 ─────────────────────────────────────
def save_progress(data, notes):
    """保存进度"""
    with open('public/data/radar-data.json', 'w', encoding='utf-8') as f:
        json.dump({
            'title': f"小红书糖尿病爆款雷达 \xb7 {datetime.now().strftime('%Y年%m月%d日')}",
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'generated_at': datetime.now().isoformat(),
            'data': {'week': notes, 'half': []},
            '_scrape_meta': data
        }, f, ensure_ascii=False, indent=2)
    print(f'  [SAVE] {len(notes)} notes saved')

def deduplicate(notes):
    seen = set()
    result = []
    for n in notes:
        if n['id'] not in seen:
            seen.add(n['id'])
            result.append(n)
    return result

def detect_patterns(note):
    title = note.get('title', '')
    patterns = []
    if any(c in title for c in '0123456789'):
        patterns.append('数字吸引')
    if any(w in title for w in ['我的', '我', '分享', '经历']):
        patterns.append('亲身经历')
    if any(w in title for w in ['?', '怎么', '如何', '为什么']):
        patterns.append('疑问引导')
    if any(w in title for w in ['干货', '方法', '技巧']):
        patterns.append('干货分享')
    if any(w in title for w in ['结果', '终于', '成功']):
        patterns.append('结果导向')
    if any(w in title for w in ['注意', '千万', '警告']):
        patterns.append('痛点警示')
    if not patterns:
        patterns.append('普通内容')
    return patterns

def detect_topic(note):
    title = (note.get('title', '') + note.get('desc', ''))[:200]
    if '1型' in title or '一型' in title:
        return '1型糖尿病'
    if '胰岛素泵' in title or ('泵' in title and len(title) < 50):
        return '胰岛素泵'
    if any(w in title for w in ['饮食', '吃', '食谱', '早餐']):
        return '糖尿病饮食'
    if any(w in title for w in ['血糖', '控糖', '监测', '动态']):
        return '血糖管理'
    return '2型糖尿病'

def make_note_normalized(raw, keyword=''):
    note_card = raw.get('note_card', raw)
    interact = note_card.get('interact_info', {})
    user = note_card.get('user', {})
    try:
        liked = int(interact.get('liked_count', 0) or 0)
    except:
        liked = 0
    return {
        'id': note_card.get('note_id', note_card.get('id', '')),
        'xsec_token': note_card.get('xsec_token', ''),
        'title': note_card.get('title', ''),
        'desc': note_card.get('desc', '')[:200],
        'author': user.get('nickname', user.get('name', 'unknown')),
        'author_avatar': user.get('avatar', ''),
        'note_type': note_card.get('type', 'normal'),
        'liked': liked,
        'collected': int(interact.get('collected_count', 0) or 0),
        'shared': int(interact.get('share_count', 0) or 0),
        'comments': int(interact.get('comment_count', 0) or 0),
        'total_engage': liked + int(interact.get('collected_count', 0) or 0) * 2,
        'topic': detect_topic(note_card),
        'boom_patterns': [],
        'link': f"https://www.xiaohongshu.com/explore/{note_card.get('note_id','')}",
        'keyword': keyword,
    }

# ─── 抓取逻辑 ─────────────────────────────────────
def fetch_search(keyword, client):
    notes = []
    for page in range(5):
        url = 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes'
        payload = {
            'keyword': keyword,
            'page_size': 20,
            'page': page + 1,
            'sort': 'general',
            'note_type': 0,
        }
        try:
            resp = client.post(url, json=payload, timeout=10)
            if resp.status_code != 200:
                print(f'  [WARN] HTTP {resp.status_code} for "{keyword}" p{page+1}')
                break
            data = resp.json()
            items = data.get('data', {}).get('items', [])
            if not items:
                break
            for item in items:
                note = make_note_normalized(item, keyword)
                if note['liked'] >= MIN_ENGAGE:
                    note['boom_patterns'] = detect_patterns(note)
                    notes.append(note)
            print(f'  [OK] "{keyword}" p{page+1}: {len(items)} items, {len(notes)} kept')
            if len(items) < 10:
                break
            time.sleep(REQUEST_DELAY + random.uniform(0, 0.5))
        except Exception as e:
            print(f'  [ERROR] "{keyword}" p{page+1}: {e}')
            break
    return notes

# ─── 主程序 ───────────────────────────────────────
def main():
    print(f'[{datetime.now().strftime("%H:%M:%S")}] Start scraping...')
    print(f'Keywords: {KEYWORDS}')
    print('-' * 40)

    transport = httpx.HTTPTransport(retries=2)
    client = httpx.Client(headers=HEADERS, timeout=30, transport=transport)

    all_notes = []
    scrape_log = []

    for kw in KEYWORDS:
        print(f'\n[SEARCH] "{kw}"')
        notes = fetch_search(kw, client)
        scrape_log.append({'keyword': kw, 'count': len(notes)})
        all_notes.extend(notes)
        time.sleep(REQUEST_DELAY + random.uniform(0.5, 1.5))

    client.close()

    unique = deduplicate(all_notes)
    print(f'\n[SUMMARY] Raw: {len(all_notes)} | Unique: {len(unique)}')
    unique.sort(key=lambda x: x.get('total_engage', 0), reverse=True)
    top = unique[:220]
    print(f'[DONE] TOP {len(top)}')

    save_progress({'keywords': KEYWORDS, 'scraped_at': datetime.now().isoformat()}, top)
    print(f'[{datetime.now().strftime("%H:%M:%S")}] Done!')

if __name__ == '__main__':
    Path('public/data').mkdir(parents=True, exist_ok=True)
    main()
