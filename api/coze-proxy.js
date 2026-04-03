// Vercel Serverless Function - Coze API 代理
// 使用 fetch API（Vercel 内置支持）

export default async function handler(req, res) {
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
    // Vercel 会自动解析 JSON body
    let bodyString;
    if (req.body) {
      bodyString = JSON.stringify(req.body);
    } else {
      // 兜底：手动读取
      const chunks = [];
      for await (const chunk of req) {
        chunks.push(chunk);
      }
      bodyString = Buffer.concat(chunks).toString();
    }

    console.log('Forwarding request to Coze API...');
    console.log('Body:', bodyString);

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
    console.log('Coze response:', responseText);

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
