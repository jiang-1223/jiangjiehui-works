// Cloudflare Worker - Coze API 代理
// 解决浏览器直接调用 Coze API 的 CORS 问题

export default {
  async fetch(request, env, ctx) {
    // 处理 CORS 预检请求
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
      });
    }

    // 只允许 POST 请求
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {
      // 获取请求体
      const body = await request.json();
      
      // 转发到 Coze API
      const cozeResponse = await fetch('https://2fd7jvzwph.coze.site/run', {
        method: 'POST',
        headers: {
          'Authorization': request.headers.get('Authorization'),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      // 获取响应
      const responseData = await cozeResponse.json();

      // 返回给浏览器（带 CORS 头）
      return new Response(JSON.stringify(responseData), {
        status: cozeResponse.status,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    }
  },
};
