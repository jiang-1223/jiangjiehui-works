const fs = require('fs');
const path = require('path');

module.exports = async (req, res) => {
  // 设置 CORS 和缓存头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');

  try {
    // 尝试多个路径（适应不同部署环境）
    const possiblePaths = [
      path.join(process.cwd(), 'public', 'data', 'radar-data.json'),
      path.join(process.cwd(), 'data', 'radar-data.json'),
      path.join(__dirname, '..', 'public', 'data', 'radar-data.json'),
      path.join(__dirname, '..', 'data', 'radar-data.json'),
    ];

    let rawData = null;
    for (const filePath of possiblePaths) {
      if (fs.existsSync(filePath)) {
        rawData = fs.readFileSync(filePath, 'utf-8');
        break;
      }
    }

    if (!rawData) {
      // 回退：从 GitHub raw 文件获取
      const githubRes = await fetch(
        'https://raw.githubusercontent.com/jiang-1223/jiangjiehui-works/main/data/radar-data.json'
      );
      if (!githubRes.ok) throw new Error('Failed to fetch from GitHub');
      rawData = await githubRes.text();
    }

    const data = JSON.parse(rawData);
    res.status(200).json(data);
  } catch (err) {
    console.error('radar-data API error:', err);
    res.status(500).json({ error: 'Failed to load data', message: err.message });
  }
};
