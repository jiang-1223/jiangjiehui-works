/**
 * 小红书糖尿病雷达数据抓取脚本
 * 监控关键词：1型糖、2型糖、胰岛素泵、CGM、美敦力、糖尿病
 */

const fs = require('fs');
const path = require('path');

// 监控关键词
const KEYWORDS = ['1型糖', '2型糖', '胰岛素泵', 'CGM', '美敦力', '糖尿病'];

// 输出路径
const OUTPUT_FILE = path.join(__dirname, 'public', 'data', 'radar-data-v4.json');

// 确保输出目录存在
const outputDir = path.dirname(OUTPUT_FILE);
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

/**
 * 模拟数据生成（实际使用时替换为真实 API 调用）
 * 实际部署时通过 GitHub Actions 调用小红书 MCP
 */
async function fetchData() {
    console.log('🔍 开始抓取小红书糖尿病相关笔记...');
    
    const notes = [];
    const now = Math.floor(Date.now() / 1000);
    
    // 为每个关键词生成一些模拟笔记
    for (const keyword of KEYWORDS) {
        for (let i = 0; i < 8; i++) {
            const note = {
                id: `${keyword}_${i}_${now}`,
                keyword: keyword,
                title: `${keyword}相关话题：${generateTitle(keyword, i)}`,
                author: generateAuthor(),
                likes: Math.floor(Math.random() * 50000) + 100,
                collects: Math.floor(Math.random() * 10000) + 50,
                comments: Math.floor(Math.random() * 2000) + 10,
                time: now - Math.floor(Math.random() * 604800), // 最近7天内
                type: Math.random() > 0.7 ? 'video' : 'image',
                cover: `https://picsum.photos/seed/${keyword}${i}/200/200`,
                url: `https://www.xiaohongshu.com/discovery/item/${note.id}`
            };
            
            notes.push(note);
        }
    }
    
    // 按点赞数排序
    notes.sort((a, b) => b.likes - a.likes);
    
    return {
        updatedAt: new Date().toISOString(),
        keywords: KEYWORDS,
        notes: notes,
        stats: {
            totalNotes: notes.length,
            avgLikes: Math.round(notes.reduce((sum, n) => sum + n.likes, 0) / notes.length),
            topKeyword: KEYWORDS[Math.floor(Math.random() * KEYWORDS.length)]
        }
    };
}

/**
 * 生成标题
 */
function generateTitle(keyword, index) {
    const templates = {
        '1型糖': [
            '我的1型糖尿病日常管理分享', '1型糖友的血糖曲线记录', '确诊1型糖尿病后的心路历程',
            '1型糖尿病患者饮食注意', '泵的使用心得与血糖控制', '1型糖宝妈的备孕经历',
            '动态血糖仪真实测评', '1型糖友的运动日记'
        ],
        '2型糖': [
            '逆转2型糖尿病的亲身经历', '二甲双胍用药感受分享', '2型糖尿病饮食食谱',
            '血糖从15降到6的方法', '2型糖友的减重之路', '空腹血糖高的原因分析',
            '适合糖友的运动推荐', '2型糖尿病并发症预防'
        ],
        '胰岛素泵': [
            '我用胰岛素泵一年的感受', '泵和打针哪个更好？', '丹纳泵和美敦力泵对比',
            '胰岛素泵使用教程', '戴泵后生活质量的改变', '泵的耗材选择建议',
            '闭环胰岛素泵体验', '胰岛素泵调泵技巧'
        ],
        'CGM': [
            '动态血糖仪真实测评', '雅培瞬感使用体验', '德康和雅培哪个准？',
            '动态血糖监测帮我控糖', 'CGM数据解读方法', '佩戴动态血糖仪的感受',
            '瞬感扫描仪使用技巧', '动态血糖图谱分析'
        ],
        '美敦力': [
            '美敦力胰岛素泵使用感受', '美敦力探头准确度测评', '美敦力泵的优势分析',
            '美敦力售后服务体验', '美敦力712泵换管操作', '美敦力耗材优惠攻略',
            '美敦力闭环系统体验', '美敦力与丹纳对比'
        ],
        '糖尿病': [
            '糖尿病患者的一日三餐', '血糖控制经验分享', '糖尿病前期逆转方法',
            '糖化血红蛋白解读', '糖尿病并发症预防', '低血糖急救经验',
            '糖尿病患者零食推荐', '血糖监测的正确方法'
        ]
    };
    
    const titles = templates[keyword] || [];
    return titles[index % titles.length] || `${keyword}相关内容分享`;
}

/**
 * 生成作者名
 */
function generateAuthor() {
    const prefixes = ['控糖小达人', '糖友圈', '健康生活', '血糖管理', '甜蜜人生'];
    const suffixes = ['儿', '妈', '控', '达人', '日记', '分享'];
    return prefixes[Math.floor(Math.random() * prefixes.length)] + 
           suffixes[Math.floor(Math.random() * suffixes.length)];
}

/**
 * 主函数
 */
async function main() {
    try {
        const data = await fetchData();
        
        // 写入 JSON 文件
        fs.writeFileSync(OUTPUT_FILE, JSON.stringify(data, null, 2), 'utf-8');
        
        console.log(`✅ 数据已保存到: ${OUTPUT_FILE}`);
        console.log(`📊 共抓取 ${data.notes.length} 条笔记`);
        console.log(`⏰ 更新时间: ${data.updatedAt}`);
        
        process.exit(0);
    } catch (error) {
        console.error('❌ 数据抓取失败:', error);
        process.exit(1);
    }
}

main();
