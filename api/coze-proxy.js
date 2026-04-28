// Vercel Serverless Function - 扣子工作流代理
// 保护 Bearer Token 不暴露在前端

const COZE_API = 'https://2fd7jvzwph.coze.site/run';
const BEARER_TOKEN = process.env.COZE_BEARER_TOKEN || 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjgwMjFiZTE3LTM4MDMtNDEwOS1hODkxLTZlOTNmZTAwOTA0ZiJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbIllFbE1vclBGTnRkWFNoN2N4dXpWWU83YlFDaExQQVpsIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzc1MTE0NTg4LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjIzNzE1MjgxNjU4OTcwMTIxIiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjI0MDU5MTA1NjE0NzU3OTMwIn0.Lt-7DyJYVwlrKxw66S59KAP9h-Q8joHWiloKqebfMu6V9SPHNRIzfUtKY11UK7YTiyrcEOfITkwXpjURbZNQCiuBkccQoEiPmFDX7ZhFCDMg2pwIdLAZTGqZ3L-f1ztPY1NCMqvRb5BdTon7yag4ogxLeiqstp1QiH74TVUt4n4p1FVnMPsDJIXxzcWKAo2ygYmWpXfRRsiySU1o2dOuwFsO7NYY7Fa_RJQ1sBQzl_S9kCCXBGfmyvtXN0Q0L9SlYHM5GR9-4pQLr_HKR8NhwDkzLoE29GrAqGUyRGcDHCqk-IQlhLowTOaXl1lrhKotN-3qVWxWORCEMglRpRr7aA';

module.exports = async (req, res) => {
    // 只允许 POST
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    // CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    try {
        const body = req.body;

        // 调用扣子 API
        const https = require('https');
        
        const postData = JSON.stringify(body || {});
        const options = {
            hostname: '2fd7jvzwph.coze.site',
            path: '/run',
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${BEARER_TOKEN}`,
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const result = await new Promise((resolve, reject) => {
            const cozeReq = https.request(options, (cozeRes) => {
                let data = '';
                cozeRes.on('data', chunk => data += chunk);
                cozeRes.on('end', () => {
                    try {
                        resolve({
                            status: cozeRes.statusCode,
                            data: JSON.parse(data)
                        });
                    } catch (e) {
                        resolve({
                            status: cozeRes.statusCode,
                            data: data
                        });
                    }
                });
            });
            cozeReq.on('error', reject);
            cozeReq.write(postData);
            cozeReq.end();
        });

        return res.status(result.status).json(result.data);

    } catch (error) {
        console.error('Coze proxy error:', error);
        return res.status(500).json({ error: '代理请求失败', detail: error.message });
    }
};
