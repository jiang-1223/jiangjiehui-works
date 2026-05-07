#!/usr/bin/env python3
"""
小红书糖尿病雷达 v4 - 数据抓取 + HTML 更新脚本
使用 xhs 库抓取数据，然后直接更新 HTML 中的内嵌数据

用法:
    python scripts/xhs_radar_v4_auto.py

环境变量:
    XHS_A1, XHS_WEB_SESSION, XHS_WEB_ID (从 GitHub Secrets 获取)
"""

import os
import json
import time
import re
import logging
from datetime import datetime
from xhs import XhsClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 搜索关键词
SEARCH_KEYWORDS = ['1型糖', '2型糖', '胰岛素泵', '美敦力', 'CGM', '糖尿病']

# 关键词→主题映射
KEYWORD_TOPIC_MAP = {
    '1型糖': '1型糖尿病',
    '2型糖': '2型糖尿病',
    '胰岛素泵': '胰岛素泵',
    '美敦力': '胰岛素泵',
    'CGM': '血糖管理',
    '糖尿病': '血糖管理',
}

# 路径
HTML_PATH = os.path.join(os.path.dirname(__file__), '..', 'public', 'xhs-radar-v4.html')
DATA_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'public', 'data', 'radar-data-v4.json')


def get_cookie_string():
    """从环境变量构建 Cookie 字符串"""
    a1 = os.getenv('XHS_A1', '')
    web_session = os.getenv('XHS_WEB_SESSION', '')
    web_id = os.getenv('XHS_WEB_ID', '')

    if not all([a1, web_session, web_id]):
        logger.error("Cookie 环境变量不完整！需要 XHS_A1, XHS_WEB_SESSION, XHS_WEB_ID")
        return None

    return f"a1={a1}; web_session={web_session}; webId={web_id}"


def search_keyword(client, keyword, page=1, page_size=20):
    """搜索单个关键词"""
    try:
        result = client.get_note_by_keyword(keyword=keyword, page=page, page_size=page_size)
        notes = []
        if result and 'items' in result:
            for item in result['items']:
                note_model = item.get('note_card', item)  # xhs 库返回的数据结构
                # 兼容两种可能的返回结构
                if isinstance(item, dict):
                    id_val = item.get('id', '') or item.get('note_id', '')
                    title = item.get('display_title', '') or item.get('title', '')
                    user = item.get('user', {})
                    author = user.get('nickname', '') if isinstance(user, dict) else str(user)
                    avatar = user.get('avatar', '') if isinstance(user, dict) else ''
                    interact = item.get('interact_info', {})
                    likes = int(interact.get('liked_count', '0'))
                    collects = int(interact.get('collected_count', '0'))
                    comments = int(interact.get('comment_count', '0'))
                    shares = int(interact.get('share_count', '0'))
                    note_type = item.get('type', 'normal')
                    cover = ''
                    image_list = item.get('image_list', [])
                    if image_list:
                        cover = image_list[0].get('url_default', '') or image_list[0].get('url', '')
                    elif item.get('video', {}).get('consumer', {}).get('origin_video_key'):
                        cover = ''

                    notes.append({
                        'id': id_val,
                        'title': title,
                        'keyword': keyword,
                        'type': 'video' if note_type == 'video' else 'image',
                        'author': author,
                        'likes': likes,
                        'collects': collects,
                        'comments': comments,
                        'shares': shares,
                        'cover': cover,
                        'url': f"https://www.xiaohongshu.com/explore/{id_val}",
                        'time': time.time(),
                        'author_avatar': avatar,
                    })
        logger.info(f'[{keyword}] 找到 {len(notes)} 条笔记')
        return notes
    except Exception as e:
        logger.error(f'[{keyword}] 搜索失败: {e}')
        return []


def process_notes(all_notes):
    """处理笔记数据：去重、计算热度、检测爆点模式"""
    # 去重
    seen = set()
    unique = []
    for n in all_notes:
        if n['id'] and n['id'] not in seen:
            seen.add(n['id'])
            unique.append(n)

    # 计算综合热度
    for n in unique:
        n['total_engage'] = round(
            n['likes'] * 1.0 + n['collects'] * 1.5 + n['comments'] * 2.0 + n['shares'] * 1.2
        )
        n['topic'] = KEYWORD_TOPIC_MAP.get(n['keyword'], '血糖管理')
        n['liked'] = n['likes']
        n['collected'] = n['collects']
        n['shared'] = n['shares']
        n['note_type'] = n['type']
        n['link'] = n['url']

        # 检测爆点模式
        patterns = []
        if re.search(r'\d', n['title']): patterns.append('数字吸引')
        if re.search(r'我|自己|亲身|经历|确诊|日记', n['title']): patterns.append('亲身经历')
        if re.search(r'[？?]', n['title']): patterns.append('疑问引导')
        if re.search(r'不要|小心|注意|避免|误区|坑', n['title']): patterns.append('痛点警示')
        if re.search(r'教程|方法|攻略|指南|干货|大全|技巧', n['title']): patterns.append('干货分享')
        if re.search(r'成功|逆转|效果|结果|变化', n['title']): patterns.append('结果导向')
        if not patterns: patterns.append('普通内容')
        n['boom_patterns'] = patterns

    # 按热度排序
    unique.sort(key=lambda x: x['total_engage'], reverse=True)
    return unique


def generate_stats(notes):
    """生成统计数据"""
    if not notes:
        return {
            'total': 0, 'max_engage': 0,
            'avg_likes': 0, 'avg_collects': 0,
            'topic_count': 0,
        }
    return {
        'total': len(notes),
        'max_engage': notes[0]['total_engage'],
        'avg_likes': round(sum(n['likes'] for n in notes) / len(notes)),
        'avg_collects': round(sum(n['collects'] for n in notes) / len(notes)),
        'topic_count': len(set(n['topic'] for n in notes)),
    }


def update_html(notes, stats):
    """更新 HTML 文件中的内嵌数据"""
    html_path = os.path.abspath(HTML_PATH)
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换 NOTES 数据
    notes_json = json.dumps(notes, ensure_ascii=False, separators=(',', ':'))
    content = re.sub(
        r'const NOTES = \[.*?\];',
        f'const NOTES = {notes_json};',
        content, flags=re.DOTALL
    )

    # 更新统计条
    max_engage_display = format_engage(stats['max_engage'])
    new_stats = (
        f'<div class="sc"><div class="sc-icon">📚</div><div><div class="sc-val">{stats["total"]}</div><div class="sc-lbl">笔记总量</div></div></div>'
        f'<div class="sc"><div class="sc-icon">🔥</div><div><div class="sc-val">{max_engage_display}</div><div class="sc-lbl">最高热度</div></div></div>'
        f'<div class="sc"><div class="sc-icon">❤️</div><div><div class="sc-val">{stats["avg_likes"]}</div><div class="sc-lbl">平均点赞</div></div></div>'
        f'<div class="sc"><div class="sc-icon">⭐</div><div><div class="sc-val">{stats["avg_collects"]}</div><div class="sc-lbl">平均收藏</div></div></div>'
        f'<div class="sc"><div class="sc-icon">🗂️</div><div><div class="sc-val">{stats["topic_count"]}</div><div class="sc-lbl">覆盖主题</div></div></div>'
    )
    content = re.sub(
        r'<div class="stats-bar">.*?</div>\s*</div>\s*<!--',
        f'<div class="stats-bar">{new_stats}</div>\n</div>\n\n<!--',
        content, flags=re.DOTALL
    )

    # 更新时间
    now_str = datetime.now().strftime('%Y/%m/%d %H:%M')
    content = re.sub(
        r"数据更新：[^<·]*",
        f"数据更新：{now_str} · 共 {stats['total']} 篇笔记",
        content
    )
    content = re.sub(
        r"更新于 [^<·]*",
        f"更新于 {now_str}",
        content
    )

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)

    logger.info(f'HTML 已更新: {html_path}')


def save_json_backup(notes):
    """保存 JSON 备份"""
    os.makedirs(os.path.dirname(DATA_JSON_PATH), exist_ok=True)
    data = {
        'notes': notes,
        'updatedAt': datetime.now().isoformat(),
        'stats': {
            'totalNotes': len(notes)
        }
    }
    with open(DATA_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f'JSON 备份已保存: {DATA_JSON_PATH}')


def format_engage(val):
    """格式化热度数值"""
    if val >= 10000:
        return f'{val/10000:.1f}万'
    elif val >= 1000:
        return f'{val/1000:.1f}k'
    return str(val)


def main():
    logger.info('=' * 50)
    logger.info('小红书糖尿病雷达 v4 - 数据抓取')
    logger.info('=' * 50)

    # 获取 Cookie
    cookie_str = get_cookie_string()
    if not cookie_str:
        logger.error('Cookie 未配置，退出')
        return False

    # 初始化客户端（不使用签名，xhs 库内部处理）
    logger.info('初始化 XhsClient...')
    try:
        client = XhsClient(
            cookie=cookie_str,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            timeout=30
        )
        logger.info('XhsClient 初始化成功')
    except Exception as e:
        logger.error(f'XhsClient 初始化失败: {e}')
        return False

    # 搜索所有关键词
    all_notes = []
    for i, kw in enumerate(SEARCH_KEYWORDS, 1):
        logger.info(f'[{i}/{len(SEARCH_KEYWORDS)}] 搜索: {kw}')
        notes = search_keyword(client, kw)
        all_notes.extend(notes)
        if i < len(SEARCH_KEYWORDS):
            time.sleep(2)  # 避免请求过快

    if not all_notes:
        logger.error('未抓取到任何笔记！')
        return False

    # 处理数据
    notes = process_notes(all_notes)
    stats = generate_stats(notes)

    logger.info(f'共抓取 {stats["total"]} 条笔记（{stats["topic_count"]} 个主题）')

    # 更新 HTML
    update_html(notes, stats)

    # 保存 JSON 备份
    save_json_backup(notes)

    logger.info('✅ 数据更新完成！')
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
