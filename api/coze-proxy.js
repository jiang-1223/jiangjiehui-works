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

    const COZE_TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjY0MmFmZTQ3LTA0NTYtNDlmNi1hNTliLWU5OTY3ZTliOWFlMiJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIllFbE1vclBGTnRkWFNoN2N4dXpWWU83YlFDaExQQVpsIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzc1MDQ2NTczLCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjIzNzE1MjgxNjU4OTcwMTIxIiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjIzNzY2OTgyODczMDU1MjY4In0.VX3b9vMVn6PKQRtIy6Y0q9xBj843LcWieWHzBnuuBzagG4_p6XGipuUkeBkyVDZzetUWdnrPbJkI_xZjqr0yi6ZPtGmGgyQhGF70cScbECK9-4g5WxvL1Cs9x0bToFqxm3LQUfYtGSFwWHE3tkwwJ6dQbYMCyFsK6zwQ0jh8nsSjc5eueNvuKYzcUsrUIzuG7t35YAFdmhHWqJUyjGSHA6gQzmLYMPsjSzJahsE7nW_rm3Lb9It_b1ECwOgtZEbzhC5hD3VfbZBlZkRpWgJsVVwYcxrvEkxwsi55i-z_GYln7EGYPt5A1g-582_dW82dFbYZCUGyrv_tw6P0u8sgDg';
    
    const cozeResponse = await fetch('https://2fd7jvzwph.coze.site/run', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + COZE_TOKEN,
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
