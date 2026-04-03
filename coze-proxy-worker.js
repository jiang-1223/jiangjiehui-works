/**
 * Cloudflare Worker 代理
 * 用于安全地代理扣子工作流 API 请求，隐藏 Token
 * 
 * 部署方式：
 * 1. 登录 https://dash.cloudflare.com → Workers & Pages
 * 2. 创建新 Worker，粘贴此代码
 * 3. 在环境变量中设置 COZE_TOKEN 和 COZE_API_URL
 * 4. 部署后，将 Worker URL 填入 xhs-workflow.html 的 PROXY_URL
 */

// 扣子工作流 API 配置（通过环境变量设置）
const COZE_API_URL = 'https://2fd7jvzwph.coze.site/run';
const COZE_TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjY0MmFmZTQ3LTA0NTYtNDlmNi1hNTliLWU5OTY3ZTliOWFlMiJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIllFbE1vclBGTnRkWFNoN2N4dXpWWU83YlFDaExQQVpsIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzc1MDQ2NTczLCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjIzNzE1MjgxNjU4OTcwMTIxIiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjIzNzY2OTgyODczMDU1MjY4In0.VX3b9vMVn6PKQRtIy6Y0q9xBj843LcWieWHzBnuuBzagG4_p6XGipuUkeBkyVDZzetUWdnrPbJkI_xZjqr0yi6ZPtGmGgyQhGF70cScbECK9-4g5WxvL1Cs9x0bToFqxm3LQUfYtGSFwWHE3tkwwJ6dQbYMCyFsK6zwQ0jh8nsSjc5eueNvuKYzcUsrUIzuG7t35YAFdmhHWqJUyjGSHA6gQzmLYMPsjSzJahsE7nW_rm3Lb9It_b1ECwOgtZEbzhC5hD3VfbZBlZkRpWgJsVVwYcxrvEkxwsi55i-z_GYln7EGYPt5A1g-582_dW82dFbYZCUGyrv_tw6P0u8sgDg';

// 允许的前端域名（CORS 白名单）
const ALLOWED_ORIGINS = [
    'https://jiangjiehui.top',
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
];

export default {
    async fetch(request, env) {
        // 处理 CORS 预检请求
        if (request.method === 'OPTIONS') {
            return handleCors(request);
        }

        // 只允许 POST 请求
        if (request.method !== 'POST') {
            return new Response(JSON.stringify({ error: 'Method not allowed' }), {
                status: 405,
                headers: { 'Content-Type': 'application/json', ...corsHeaders(request) }
            });
        }

        try {
            // 读取前端请求体
            const body = await request.json();

            // 转发到扣子 API
            const cozeResponse = await fetch(COZE_API_URL, {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer ' + COZE_TOKEN,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    requirement: body.requirement || '',
                    image: body.image || '',
                }),
            });

            const responseData = await cozeResponse.json();

            return new Response(JSON.stringify(responseData), {
                status: cozeResponse.status,
                headers: {
                    'Content-Type': 'application/json',
                    ...corsHeaders(request),
                }
            });

        } catch (error) {
            return new Response(JSON.stringify({ error: error.message }), {
                status: 500,
                headers: {
                    'Content-Type': 'application/json',
                    ...corsHeaders(request),
                }
            });
        }
    }
};

function corsHeaders(request) {
    const origin = request.headers.get('Origin') || '';
    const isAllowed = ALLOWED_ORIGINS.some(allowed => origin.startsWith(allowed));

    if (isAllowed) {
        return {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        };
    }

    // 开发环境允许所有来源
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    };
}

function handleCors(request) {
    return new Response(null, {
        status: 204,
        headers: corsHeaders(request),
    });
}
