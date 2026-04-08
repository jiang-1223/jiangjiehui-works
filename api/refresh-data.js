/**
 * 小红书数据雷达 - 数据刷新端点
 * 由 Vercel Cron 每周调用，或手动触发
 * 路径：api/refresh-data.js
 */
const fs = require('fs');
const path = require('path');
const https = require('https');

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST' && req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Vercel Cron 会自动设置 VERCEL_ENV = 'production' 和 headers
  const isCron = req.headers['x-vercel-cron'] === 'true';

  if (isCron) {
    console.log('[Cron] Starting scheduled data refresh...');
  } else {
    console.log('[Manual] Starting manual data refresh...');
  }

  try {
    // 读取现有数据
    const dataPath = path.join(__dirname, '..', 'public', 'data', 'radar-data.json');
    let data;

    try {
      const raw = fs.readFileSync(dataPath, 'utf-8');
      data = JSON.parse(raw);
    } catch (e) {
      data = { weekly: [], monthly: [], last_updated: null };
    }

    // 更新时间戳
    data.last_updated = new Date().toISOString();

    // 尝试从 XHS 抓取新数据
    // 注意：需要将 XHS Cookie 设置为 Vercel 环境变量 XHS_COOKIE
    const cookie = process.env.XHS_COOKIE;
    const xhsData = await fetchXHSData(cookie);

    if (xhsData && xhsData.length > 0) {
      const today = new Date().toISOString().split('T')[0];
      const newWeekly = {
        date: today,
        notes: xhsData,
        fetched_at: new Date().toISOString()
      };
      data.weekly.unshift(newWeekly);
      // 只保留最近 12 周
      data.weekly = data.weekly.slice(0, 12);
      console.log(`[XHS] Fetched ${xhsData.length} notes`);
    } else {
      console.log('[XHS] No new data (cookie may be missing or API changed)');
    }

    // 写回文件
    fs.writeFileSync(dataPath, JSON.stringify(data, null, 2), 'utf-8');
    console.log('[Done] Data file updated');

    res.status(200).json({
      success: true,
      refreshed: !!xhsData,
      last_updated: data.last_updated,
      note: isCron ? 'Auto-refresh by Vercel Cron' : 'Manual refresh'
    });

  } catch (err) {
    console.error('[Error]', err);
    res.status(500).json({ error: 'Refresh failed', message: err.message });
  }
};

/**
 * 抓取小红书数据
 * @param {string} cookie - XHS Cookie
 * @returns {Promise<Array>} 笔记列表
 */
function fetchXHSData(cookie) {
  return new Promise((resolve) => {
    if (!cookie) {
      console.log('[XHS] No cookie configured, skipping fetch');
      resolve([]);
      return;
    }

    // 修复：移除cookie值中的多余空格（有些cookie被截断时带空格）
    const cleanCookie = cookie.replace(/\s+/g, ' ').trim();

    const keywords = ['1型糖尿病', '胰岛素泵', '硅基动态'];
    const results = [];

    // 并行抓取多个关键词
    let completed = 0;
    const total = keywords.length;

    keywords.forEach((kw) => {
      const url = `https://edith.xiaohongshu.com/api/sns/web/v3/search/notes?keyword=${encodeURIComponent(kw)}&page=1&page_size=10&search_id=&sort=general&note_type=0`;

      const options = {
        hostname: 'edith.xiaohongshu.com',
        path: `/api/sns/web/v3/search/notes?keyword=${encodeURIComponent(kw)}&page=1&page_size=10&search_id=&sort=general&note_type=0`,
        method: 'GET',
        headers: {
          'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
          'Cookie': cleanCookie,
          'Referer': 'https://www.xiaohongshu.com/',
          'Accept': 'application/json, text/plain, */*',
        }
      };

      const req = https.request(options, (r) => {
        let body = '';
        r.on('data', (chunk) => body += chunk);
        r.on('end', () => {
          try {
            const parsed = JSON.parse(body);
            if (parsed.data?.notes) {
              parsed.data.notes.forEach(note => {
                results.push({
                  id: note.note_id,
                  title: note.title || note.display_title,
                  author: note.user?.nickname,
                  likes: note.interact_info?.liked_count || 0,
                  collects: note.interact_info?.collected_count || 0,
                  keyword: kw,
                  url: `https://www.xiaohongshu.com/explore/${note.note_id}`,
                  fetched_at: new Date().toISOString()
                });
              });
            }
          } catch (e) {
            console.log(`[XHS] Failed to parse response for "${kw}": ${e.message}`);
          }
          completed++;
          if (completed === total) resolve(results);
        });
      });

      req.on('error', (e) => {
        console.log(`[XHS] Request error for "${kw}": ${e.message}`);
        completed++;
        if (completed === total) resolve(results);
      });

      req.setTimeout(8000, () => {
        req.destroy();
        completed++;
        if (completed === total) resolve(results);
      });

      req.end();
    });
  });
}
