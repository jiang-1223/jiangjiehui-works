/**
 * 小红书数据雷达 - Serverless API 端点
 * 路径：api/radar-data.js
 * 返回 public/data/radar-data.json 的内容
 */
const fs = require('fs');
const path = require('path');

module.exports = (req, res) => {
  // CORS 头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const jsonPath = path.join(__dirname, '..', 'public', 'data', 'radar-data.json');
    const data = fs.readFileSync(jsonPath, 'utf-8');
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.setHeader('Cache-Control', 'public, max-age=300'); // 缓存5分钟
    res.status(200).send(data);
  } catch (err) {
    console.error('Error reading radar data:', err);
    res.status(500).json({ error: 'Failed to load data', message: err.message });
  }
};
