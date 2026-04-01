// Vercel Serverless Function - Coze API 代理
// 解决浏览器直接调用 Coze API 的 CORS 问题

const https = require('https');

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
    const bodyString = JSON.stringify(req.body);
    
    const options = {
      hostname: '2fd7jvzwph.coze.site',
      port: 443,
      path: '/run',
      method: 'POST',
      headers: {
        'Authorization': req.headers.authorization || '',
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(bodyString)
      }
    };

    const cozeResponse = await new Promise((resolve, reject) => {
      const proxyReq = https.request(options, (proxyRes) => {
        let data = '';
        proxyRes.on('data', chunk => data += chunk);
        proxyRes.on('end', () => {
          try {
            resolve({
              status: proxyRes.statusCode,
              data: JSON.parse(data)
            });
          } catch (e) {
            resolve({
              status: proxyRes.statusCode,
              data: data
            });
          }
        });
      });
      proxyReq.on('error', reject);
      proxyReq.write(bodyString);
      proxyReq.end();
    });

    return res.status(cozeResponse.status).json(cozeResponse.data);
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
};
