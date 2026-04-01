// Vercel Serverless Function - Coze API 代理
// 解决浏览器直接调用 Coze API 的 CORS 问题

module.exports = async function handler(req, res) {
  // 设置 CORS 头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // 处理预检请求
  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  // 只允许 POST 请求
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // 转发到 Coze API
    const cozeResponse = await fetch('https://2fd7jvzwph.coze.site/run', {
      method: 'POST',
      headers: {
        'Authorization': req.headers.authorization,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body),
    });

    // 获取响应
    const responseData = await cozeResponse.json();

    // 返回给浏览器
    return res.status(cozeResponse.status).json(responseData);
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
};
