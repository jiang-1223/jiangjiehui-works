/**
 * 糖尿病爆款雷达 v4 - 数据刷新端点
 * 路径：api/refresh-radar.js
 *
 * 从小红书搜索API抓取最新数据，返回JSON给前端
 */
const https = require('https');

const XHS_COOKIE = process.env.XHS_COOKIE;

// 关键词→主题映射
const KEYWORD_TOPIC_MAP = {
  '1型糖': '1型糖尿病',
  '2型糖': '2型糖尿病',
  '1型糖尿病': '1型糖尿病',
  '2型糖尿病': '2型糖尿病',
  '胰岛素泵': '胰岛素泵',
  '美敦力': '胰岛素泵',
  'CGM': '血糖管理',
  '糖尿病': '血糖管理',
  '血糖仪': '血糖管理',
  '血糖管理': '血糖管理'
};

// 搜索关键词列表
const SEARCH_KEYWORDS = ['1型糖', '2型糖', '胰岛素泵', '美敦力', 'CGM', '糖尿病'];

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ ok: false, msg: 'Method not allowed' });

  if (!XHS_COOKIE) {
    return res.status(200).json({
      ok: false,
      msg: 'XHS_COOKIE 未配置，无法从服务端抓取数据。请在本地运行 WorkBuddy MCP 抓取数据后更新。'
    });
  }

  try {
    console.log('[refresh-radar] Starting data refresh...');
    const notes = await fetchAllKeywords();
    console.log('[refresh-radar] Fetched', notes.length, 'notes');

    if (notes.length === 0) {
      return res.status(200).json({ ok: false, msg: '未获取到新数据，小红书接口可能已更新' });
    }

    // 计算综合热度
    notes.forEach(n => {
      n.total_engage = (n.likes || 0) * 1.0 + (n.collects || 0) * 1.5 + (n.comments || 0) * 2.0 + (n.shares || 0) * 1.2;
      n.topic = KEYWORD_TOPIC_MAP[n.keyword] || '血糖管理';

      // 自动检测爆点模式
      const patterns = [];
      if (/\d/.test(n.title)) patterns.push('数字吸引');
      if (/我|自己|亲身|经历|确诊|日记/.test(n.title)) patterns.push('亲身经历');
      if (/[？?]/.test(n.title)) patterns.push('疑问引导');
      if (/不要|小心|注意|避免|误区|坑/.test(n.title)) patterns.push('痛点警示');
      if (/教程|方法|攻略|指南|干货|大全|技巧/.test(n.title)) patterns.push('干货分享');
      if (/成功|逆转|效果|结果|变化/.test(n.title)) patterns.push('结果导向');
      if (patterns.length === 0) patterns.push('普通内容');
      n.boom_patterns = patterns;
    });

    const now = new Date();
    const timeStr = now.getFullYear() + '/' +
      String(now.getMonth() + 1).padStart(2, '0') + '/' +
      String(now.getDate()).padStart(2, '0') + ' ' +
      String(now.getHours()).padStart(2, '0') + ':' +
      String(now.getMinutes()).padStart(2, '0');

    // 统计
    const maxEngage = Math.max(...notes.map(n => n.total_engage));
    const avgLikes = Math.round(notes.reduce((s, n) => s + (n.likes || 0), 0) / notes.length);
    const avgCollects = Math.round(notes.reduce((s, n) => s + (n.collects || 0), 0) / notes.length);
    const topics = [...new Set(notes.map(n => n.topic))];

    res.status(200).json({
      ok: true,
      notes: notes,
      stats: {
        total: notes.length,
        max_engage: maxEngage,
        avg_likes: avgLikes,
        avg_collects: avgCollects,
        topic_count: topics.length,
        updated_at: timeStr
      }
    });
  } catch (err) {
    console.error('[refresh-radar] Error:', err);
    res.status(200).json({ ok: false, msg: '抓取失败: ' + err.message });
  }
};

/**
 * 搜索所有关键词
 */
function fetchAllKeywords() {
  return new Promise((resolve) => {
    const results = [];
    let completed = 0;
    const total = SEARCH_KEYWORDS.length;

    SEARCH_KEYWORDS.forEach((kw) => {
      fetchKeyword(kw)
        .then(notes => {
          results.push(...notes);
          console.log(`[refresh-radar] "${kw}": ${notes.length} notes`);
        })
        .catch(e => console.log(`[refresh-radar] "${kw}" error: ${e.message}`))
        .finally(() => {
          completed++;
          if (completed === total) {
            // 去重（按id）
            const seen = new Set();
            const unique = results.filter(n => {
              if (seen.has(n.id)) return false;
              seen.add(n.id);
              return true;
            });
            resolve(unique);
          }
        });
    });
  });
}

/**
 * 搜索单个关键词
 */
function fetchKeyword(keyword) {
  return new Promise((resolve, reject) => {
    const cleanCookie = XHS_COOKIE.replace(/\s+/g, ' ').trim();
    const encodedKw = encodeURIComponent(keyword);

    const opts = {
      hostname: 'edith.xiaohongshu.com',
      path: `/api/sns/web/v3/search/notes?keyword=${encodedKw}&page=1&page_size=20&sort=general&note_type=0`,
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Cookie': cleanCookie,
        'Referer': 'https://www.xiaohongshu.com/',
        'Accept': 'application/json, text/plain, */*',
      }
    };

    const req = https.request(opts, (r) => {
      let body = '';
      r.on('data', c => body += c);
      r.on('end', () => {
        try {
          const parsed = JSON.parse(body);
          const notes = [];
          if (parsed.data?.notes) {
            parsed.data.notes.forEach(note => {
              const interact = note.interact_info || {};
              const cover = note.image_list?.[0]?.url_default ||
                            note.video?.consumer?.origin_video_key ||
                            '';
              notes.push({
                id: note.note_id,
                title: note.title || note.display_title || '无标题',
                keyword: keyword,
                note_type: note.type === 'video' ? 'video' : 'image',
                author: note.user?.nickname || '匿名用户',
                author_avatar: note.user?.avatar || '',
                likes: parseInt(interact.liked_count || '0'),
                collects: parseInt(interact.collected_count || '0'),
                comments: parseInt(interact.comment_count || '0'),
                shares: parseInt(interact.share_count || '0'),
                cover: cover,
                link: `https://www.xiaohongshu.com/explore/${note.note_id}`,
                time: Date.now() / 1000
              });
            });
          }
          resolve(notes);
        } catch (e) {
          reject(new Error('JSON parse error for "' + keyword + '"'));
        }
      });
    });

    req.on('error', e => reject(e));
    req.setTimeout(12000, () => { req.destroy(); reject(new Error('timeout')); });
    req.end();
  });
}
