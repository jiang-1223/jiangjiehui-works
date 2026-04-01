// 最简单的 Coze API 代理
export default async function handler(req, res) {
  // 设置 CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    console.log('Forwarding to Coze API...');
    
    // 直接转发，完全不变
    const cozeResponse = await fetch('https://2fd7jvzwph.coze.site/run', {
      method: 'POST',
      headers: {
        'Authorization': req.headers.authorization || '',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req.body)
    });
    
    const data = await cozeResponse.text();
    console.log('Coze response status:', cozeResponse.status);
    
    // 返回相同的状态码和数据
    res.status(cozeResponse.status);
    res.setHeader('Content-Type', 'application/json');
    res.send(data);
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ 
      error: error.message,
      note: '检查 Vercel 日志查看详细错误' 
    });
  }
}