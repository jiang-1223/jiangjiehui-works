/**
 * 小红书雷达数据 - 刷新端点
 * GET/POST /api/refresh-data
 *
 * 功能：
 * 1. 触发 GitHub Actions workflow，重新抓取小红书数据
 * 2. 更新 xhs_diabetes_data.json 数据文件
 * 3. 触发重新生成 xhs_radar_v3.html 页面
 * 4. Vercel 自动部署上线
 */
const https = require('https');

const GITHUB_TOKEN = process.env.GITHUB_TOKEN || process.env.PERSONAL_ACCESS_TOKEN;
const REPO_OWNER = 'jiang-1223';
const REPO_NAME = 'jiangjiehui-works';

const WF_WORKFLOW_ID = 'xhs-radar-refresh.yml'; // GitHub Actions workflow 文件名
const DATA_FILE_PATH = 'xhs_diabetes_data.json'; // 根目录的原始数据文件

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST' && req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  console.log('[Refresh] Request received:', req.method);

  // 如果有 GitHub Token，触发 workflow
  if (GITHUB_TOKEN) {
    try {
      console.log('[Refresh] Triggering GitHub Actions workflow...');
      const wfResult = await triggerWorkflow();
      console.log('[Refresh] Workflow triggered:', wfResult);

      res.status(200).json({
        ok: true,
        message: '数据刷新任务已启动，GitHub Actions 正在抓取小红书最新数据，完成后页面将自动更新。预计 2-3 分钟上线。',
        workflow: wfResult,
        deployed_url: 'https://jiangjiehui.top/assets/reports/xhs_radar_v3.html'
      });
      return;
    } catch (err) {
      console.error('[Refresh] Workflow trigger failed:', err);
      res.status(200).json({
        ok: false,
        error: '触发刷新失败: ' + err.message,
        hint: '可前往 GitHub Actions 手动触发: https://github.com/jing-1223/jiangjiehui-works/actions'
      });
      return;
    }
  }

  // 无 Token 时返回说明
  res.status(200).json({
    ok: false,
    error: '未配置 GitHub Token，无法自动刷新',
    message: '请在 Vercel 环境变量中配置 PERSONAL_ACCESS_TOKEN 以启用自动刷新功能。',
    manual_url: 'https://github.com/jing-1223/jiangjiehui-works/actions'
  });
};

/**
 * 触发 GitHub Actions workflow
 */
function githubApi(method, path, body) {
  return new Promise((resolve, reject) => {
    const bodyStr = body ? JSON.stringify(body) : '';
    const opts = {
      hostname: 'api.github.com',
      path,
      method,
      headers: {
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
        'User-Agent': 'XHS-Radar-Bot'
      }
    };
    if (bodyStr) {
      opts.headers['Content-Length'] = Buffer.byteLength(bodyStr);
    }
    const req = https.request(opts, (r) => {
      let data = '';
      r.on('data', c => data += c);
      r.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (r.statusCode >= 200 && r.statusCode < 300) {
            resolve(parsed);
          } else {
            reject(new Error(`GitHub API ${method} ${path} failed: ${r.statusCode} ${parsed.message || data.slice(0, 100)}`));
          }
        } catch (e) {
          reject(new Error(`GitHub API parse error: ${data.slice(0, 100)}`));
        }
      });
    });
    req.on('error', reject);
    if (bodyStr) req.write(bodyStr);
    req.end();
  });
}

async function triggerWorkflow() {
  // 列出 workflow runs，找到 xhs-radar-refresh
  const runs = await githubApi('GET', `/repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows/${WF_WORKFLOW_ID}/runs`);

  if (runs.workflow_runs && runs.workflow_runs.length > 0) {
    const latestRun = runs.workflow_runs[0];
    // 如果正在运行，返回状态
    if (latestRun.status === 'in_progress' || latestRun.status === 'queued') {
      return {
        status: latestRun.status,
        run_id: latestRun.id,
        html_url: latestRun.html_url,
        message: '刷新任务正在进行中，请稍候…'
      };
    }
  }

  // 触发新 workflow
  const triggerResult = await githubApi('POST', `/repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows/${WF_WORKFLOW_ID}/dispatches`, {
    ref: 'main',
    inputs: {
      trigger_type: { value: 'manual' }
    }
  });

  return {
    status: 'triggered',
    message: '刷新任务已触发，预计 2-3 分钟完成',
    check_url: `https://github.com/${REPO_OWNER}/${REPO_NAME}/actions`
  };
}
