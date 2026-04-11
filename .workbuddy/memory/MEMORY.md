# 项目长期记忆

## 项目结构

### 小红书糖尿病雷达 v4
- **工作流**：`.github/workflows/xhs-diabetes-radar-v4.yml`
- **脚本**：`scripts/xhs_crawler.py`（使用 xhs Python 库）
- **HTML**：`public/xhs-radar-v4.html`（唯一可访问版本）
- **数据**：`public/data/radar-data-v4.json`
- **存档**：`assets/reports/xhs_diabetes_radar_v4.html`（仅 GitHub 存储）
- **访问地址**：https://jiangjiehui.top/xhs-radar-v4.html

**重要约定**：
- ✅ 只维护 v4 版本，不再创建 v5、v6 等新版本
- ✅ HTML 必须放在 `public/` 目录下才能被 Vercel 部署
- ❌ `assets/reports/` 不会被 Vercel 部署，只用于 GitHub 存档
- ❌ 已删除所有 v2、v3、daily 版本的文件

### 密钥存储
以下密钥已保存在 GitHub Secrets 中，无需再次询问：
- **XHS_A1**: 小红书 Cookie（a1 值）
- **XHS_WEB_SESSION**: 小红书 Cookie（web_session 值）
- **XHS_WEB_ID**: 小红书 Cookie（webId 值）
- **GH_TOKEN**: GitHub Personal Access Token
- **VERCEL_DEPLOY_HOOK**: Vercel 自动部署钩子

### 自动化任务
- **小红书糖尿病雷达v4周更新**：每周一 09:00 自动运行
  - 工作区：d:\腾讯小龙虾任务
  - 触发 Vercel 部署

## 技术栈

### 前端
- 静态网站部署：Vercel
- HTML/CSS/JavaScript（原生）
- 数据可视化：Chart.js

### 后端
- Python 3.11
- xhs 库（小红书数据抓取）
- GitHub Actions 自动化

## 踩坑记录

### Vercel 部署路径问题
- ❌ 错误：把 HTML 放到 `assets/reports/` → 无法访问
- ✅ 正确：把 HTML 放到 `public/` → 可以访问
- 已犯过 2 次错误，务必记住！

### Git 历史冲突
- 本地提交和远程提交冲突时，使用 `git pull --rebase` 解决
- 工作流会自动推送数据更新，需要先拉取再推送

### 工作流权限问题
- GitHub Actions 需要 `permissions: contents: write` 才能推送
- checkout 步骤需要使用 `token: ${{ secrets.GH_TOKEN }}`

## 用户偏好

### 称呼
- 叫她"富婆"，不要叫"泡泡"

### 沟通风格
- 温暖、活泼、直接
- 需要严谨时严谨，需要轻松时轻松
- 每次聊天结束时关心她的学习进度

### 工作习惯
- 希望我记住密钥，不要每次都问她要
- 希望我先自己验证链接，确认可用后再告诉她
- 不喜欢重复犯错，需要我总结经验
