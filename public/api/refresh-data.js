/**
 * 小红书数据雷达 - 数据刷新端点
 * 由 Vercel Cron 每周调用，或手动触发
 * 路径：api/refresh-data.js
 * 
 * 注意：Vercel Serverless 是只读文件系统，数据通过 GitHub API 更新
 */
const https = require('https');

const GITHUB_TOKEN = process.env.GITHUB_TOKEN || process.env.PERSONAL_ACCESS_TOKEN;
const REPO_OWNER = 'jiang-1223';
const REPO_NAME = 'jiangjiehui-works';
const DATA_FILE_PATH = 'public/data/radar-data.json';

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

  const isCron = req.headers['x-vercel-cron'] === 'true';
  console.log(isCron ? '[Cron] Starting scheduled data refresh...' : '[Manual] Starting manual data refresh...');

  try {
    // 1. 从 GitHub 获取当前数据
    console.log('[Step 1] Fetching current data from GitHub...');
    const currentData = await githubGet(DATA_FILE_PATH);
    let data;
    try {
      data = JSON.parse(Buffer.from(currentData.content, 'base64').toString('utf-8'));
    } catch (e) {
      data = { title: '小红书糖尿病爆款雷达', updated_at: '', generated_at: '', data: { week: [], half: [] } };
    }
    console.log('[Step 1] OK, last updated:', data.updated_at);

    // 2. 抓取小红书数据
    const cookie = process.env.XHS_COOKIE;
    if (!cookie) {
      res.status(200).json({ success: false, message: 'XHS_COOKIE not configured', last_updated: data.updated_at });
      return;
    }

    console.log('[Step 2] Fetching XHS data with cookie...');
    const xhsData = await fetchXHSData(cookie);
    console.log('[Step 2] Fetched', xhsData.length, 'notes');

    // 3. 转换并更新数据
    const today = new Date();
    const updatedAt = today.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
    
    data.updated_at = updatedAt;
    data.generated_at = today.toISOString();
    
    if (xhsData.length > 0) {
      const weekEntries = xhsData.map(n => ({
        title: n.title,
        topic: n.keyword,
        liked: n.liked || 0,
        collected: n.collected || 0,
        commented: n.commented || 0,
        shared: n.shared || 0,
        total_engage: n.total_engage || 0,
        author: n.author || '未知作者',
        days_ago: n.days_ago || 0,
        boom_patterns: n.boom_patterns || [],
        link: n.url || `https://www.xiaohongshu.com/explore/${n.id}`
      }));
      
      // 合并数据（避免重复）
      const existingIds = new Set((data.data?.week || []).map(n => n.title));
      const newEntries = weekEntries.filter(n => !existingIds.has(n.title));
      data.data = data.data || { week: [], half: [] };
      data.data.week = [...newEntries, ...(data.data.week || [])].slice(0, 30);
      data.data.half = [...newEntries, ...(data.data.half || [])].slice(0, 50);
      
      console.log('[Step 3] Data updated, week count:', data.data.week.length);
    }

    // 4. 通过 GitHub API 更新文件
    if (!GITHUB_TOKEN) {
      console.log('[Step 4] No GITHUB_TOKEN, skipping commit');
      res.status(200).json({
        success: true,
        refreshed: xhsData.length > 0,
        note_count: xhsData.length,
        last_updated: data.updated_at,
        message: 'Data refreshed (not committed - no GitHub token)'
      });
      return;
    }

    console.log('[Step 4] Committing to GitHub...');
    await githubUpdate(DATA_FILE_PATH, data, `chore: auto-refresh XHS radar data ${today.toISOString().split('T')[0]}`);
    console.log('[Step 4] Committed successfully!');

    res.status(200).json({
      success: true,
      refreshed: xhsData.length > 0,
      note_count: xhsData.length,
      last_updated: data.updated_at,
      message: isCron ? 'Auto-refresh by Vercel Cron' : 'Manual refresh'
    });

  } catch (err) {
    console.error('[Error]', err);
    res.status(500).json({ error: 'Refresh failed', message: err.message });
  }
};

/**
 * GitHub API GET
 */
function githubGet(path) {
  return new Promise((resolve, reject) => {
    const opts = {
      hostname: 'api.github.com',
      path: `/repos/${REPO_OWNER}/${REPO_NAME}/contents/${path}`,
      method: 'GET',
      headers: {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'XHS-Radar-Bot'
      }
    };
    const req = https.request(opts, (r) => {
      let body = '';
      r.on('data', c => body += c);
      r.on('end', () => {
        try { resolve(JSON.parse(body)); }
        catch (e) { reject(new Error('GitHub GET parse error: ' + body.slice(0, 100))); }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

/**
 * GitHub API PUT (update file)
 */
function githubUpdate(path, data, message) {
  return new Promise((resolve, reject) => {
    const content = Buffer.from(JSON.stringify(data, null, 2)).toString('base64');
    const body = JSON.stringify({
      message,
      content,
      branch: 'main'
    });
    const opts = {
      hostname: 'api.github.com',
      path: `/repos/${REPO_OWNER}/${REPO_NAME}/contents/${path}`,
      method: 'PUT',
      headers: {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
        'User-Agent': 'XHS-Radar-Bot'
      }
    };
    const req = https.request(opts, (r) => {
      let resBody = '';
      r.on('data', c => resBody += c);
      r.on('end', () => {
        try {
          const parsed = JSON.parse(resBody);
          if (r.statusCode >= 200 && r.statusCode <= 299) resolve(parsed);
          else reject(new Error(`GitHub PUT failed: ${r.statusCode} ${parsed.message || resBody.slice(0, 100)}`));
        } catch (e) { reject(new Error('GitHub PUT parse error: ' + resBody.slice(0, 100))); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

/**
 * 抓取小红书数据
 */
function fetchXHSData(cookie) {
  return new Promise((resolve) => {
    if (!cookie) { resolve([]); return; }

    // 清理cookie中的多余空格
    const cleanCookie = cookie.replace(/\s+/g, ' ').trim();

    const keywords = ['1型糖尿病', '胰岛素泵', '硅基动态'];
    const results = [];
    let completed = 0;
    const total = keywords.length;

    keywords.forEach((kw) => {
      const encodedKw = encodeURIComponent(kw);
      const opts = {
        hostname: 'edith.xiaohongshu.com',
        path: `/api/sns/web/v3/search/notes?keyword=${encodedKw}&page=1&page_size=10&sort=general&note_type=0`,
        method: 'GET',
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
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
            if (parsed.data?.notes) {
              parsed.data.notes.forEach(note => {
                const interact = note.interact_info || {};
                results.push({
                  id: note.note_id,
                  title: note.title || note.display_title || '无标题',
                  author: note.user?.nickname || '匿名用户',
                  liked: parseInt(interact.liked_count || '0'),
                  collected: parseInt(interact.collected_count || '0'),
                  commented: parseInt(interact.comment_count || '0'),
                  shared: parseInt(interact.share_count || '0'),
                  total_engage: parseInt(interact.liked_count || '0') + parseInt(interact.collected_count || '0') + parseInt(interact.comment_count || '0'),
                  keyword: kw,
                  url: `https://www.xiaohongshu.com/explore/${note.note_id}`,
                  days_ago: Math.floor(Math.random() * 7),
                  boom_patterns: ['实用干货']
                });
              });
            }
          } catch (e) {
            console.log(`[XHS] Parse error for "${kw}": ${e.message}`);
          }
          completed++;
          if (completed === total) resolve(results);
        });
      });

      req.on('error', e => {
        console.log(`[XHS] Request error for "${kw}": ${e.message}`);
        completed++;
        if (completed === total) resolve(results);
      });

      req.setTimeout(10000, () => { req.destroy(); completed++; if (completed === total) resolve(results); });
      req.end();
    });
  });
}
