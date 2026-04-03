// Coze API 代理 - 简化版
// 解决跨域问题并正确处理请求体

export const config = {
  api: {
    bodyParser: true,  // 启用 body 解析
  }
};

export default async function handler(req, res) {
  // 设置 CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // 处理预检请求
  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  // 只允许 POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    console.log('Received request:', JSON.stringify(req.body, null, 2));

    // Vercel 会自动解析 JSON body 到 req.body
    const bodyString = JSON.stringify(req.body);

    console.log('Forwarding to Coze API...');

    const cozeResponse = await fetch('https://2fd7jvzwph.coze.site/run', {
      method: 'POST',
      headers: {
        'Authorization': req.headers.authorization || '',
        'Content-Type': 'application/json',
      },
      body: bodyString
    });

    const responseText = await cozeResponse.text();
    console.log('Coze response status:', cozeResponse.status);
    console.log('Coze response:', responseText.substring(0, 500));

    res.status(cozeResponse.status);
    res.setHeader('Content-Type', 'application/json');
    res.send(responseText);

  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({
      error: error.message,
      stack: error.stack
    });
  }
}
