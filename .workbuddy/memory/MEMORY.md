# MEMORY.md - 泡泡的记忆库

## 关于泡泡

- 真名: 蒋洁慧，1997年出生
- 工作经历: 新媒体运营、私域运营
- 目前最大目标: 换工作涨薪（优先级最高！），想跳槽去AI行业
- 兴趣爱好: 布艺手工（会周末摆摊）、养了两只乌龟、跳舞2年
- 性格: 活泼可爱

## 账号信息

### 公众号
- 公众号名称: 春日泡泡
- 公众号原始ID: gh_049c19510355
- AppID: wx6357d8acbc7ec32b
- biz参数: MzU0MTM4MzU5Mw==

**公众号文章同步到IMA知识库：**
- 2026-03-31: 成功导入第一篇文章到个人知识库
- 公众号API权限受限，需手动复制链接导入
- 存储位置: IMA"个人知识库"

### 自媒体矩阵
- 抖音带货: 29288502737
- 抖音乌龟: 31917247996
- 小红书美食: 2万赞
- 小红书布艺: 8441赞

## 项目

### AI作品集网站
- 已成功部署到公网: https://jiangjiehui.top
- GitHub仓库: https://github.com/jiang-1223/jiangjiehui-works
- 使用GitHub + Vercel + 腾讯云DNS方案
- 2026-04-03 当前保留的代表性公开成果页：小红书数据雷达 `https://jiangjiehui.top/assets/reports/xhs_radar_v2.html`、扣子工作流页面 `https://www.jiangjiehui.top/coze-workflow.html`
- 2026-04-03 已下线旧页面：`https://www.jiangjiehui.top/radar/`、`https://www.jiangjiehui.top/assets/reports/xhs_diabetes_report.html`、`https://www.jiangjiehui.top/xhs-workflow-api.html`、`https://www.jiangjiehui.top/xhs-workflow.html`、`https://www.jiangjiehui.top/xhs-workflow-simple.html`
- 2026-04-03 IMA OpenAPI 凭证已配置：Client ID = `63060e2bb1135b1aae26139a13bd1d8b`，API Key 已写入用户环境变量
- IMA 笔记《工作成果合集》已创建，笔记 ID: `7445813483564433`，包含两个保留成果页：小红书数据雷达和扣子工作流页面
- 2026-04-03 21:36 页面更新：
  1. 删除统计卡片区域（30天AI学习/2万+/7+/365天）及其所有CSS样式
  2. 公众号按钮改为点击显示二维码弹窗（需手动添加 assets/wechat-qrcode.png）
  3. Week 3 学习成果卡片链接调整为本地 coze-workflow.html 页面
  4. 页脚添加精确更新时间（以后每次修改需更新此时间）
  5. 作品展示板块标题修改为「AI数据工具」，删除板块描述
  6. 删除 Week 2 和 Week 3 学习成果描述文字
  7. 30天AI学习卡片改为链接跳转 ai_learning_plan.html
  8. OpenClaw卡片改为「扣子智能体搭建」，链接到Coze商店，添加SVG封面
  9. 扣子Coze Bot卡片描述改为「个性化小红书宣传文案生成」，更新链接，添加SVG封面
- IMA笔记《工作成果合集》已补充三个新链接及原有链接说明


### 自动化任务
1. 1型糖尿病每日晨报 - 每天早上发送，包含小红书热门笔记+全网热点资讯，发送至1760893265@qq.com
2. 美敦力运营晨报 - 工作日09:05发送

## 偏好
- 每次聊天结束时，关心她的学习进度
- 喜欢温暖、活泼的交流风格
- 做事认真，追求效率

## 踩坑经验

### 2026-04-01 扣子工作流API代理
- **Vercel Serverless Function 代理**：`req.body` 不会自动解析 JSON，必须用 `for await (const chunk of req)` 手动读取
- **base64图片传输**：Coze API 支持 base64 格式的图片 URL，不需要图床
- **分支同步**：Vercel 默认使用 `main` 分支，如果推送到 `master` 需要同步到 `main`
