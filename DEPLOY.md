# 🚀 部署指南：小红书文案生成器

## 文件说明

需要上传到 GitHub 仓库的文件：

| 文件 | 用途 | 放置位置 |
|------|------|---------|
| `xhs-workflow.html` | 文案生成器前端页面 | 仓库根目录 |
| `coze-proxy-worker.js` | Cloudflare Worker 代理（隐藏 Token） | 部署到 Cloudflare Workers |
| `index.html` | 修改后的首页（替换工作流卡片） | 仓库根目录（覆盖原文件） |

---

## 第一步：上传文件到 GitHub

### 方法 A：GitHub 网页端上传（推荐，最简单）

1. 打开 https://github.com/jiang-1223/jiangjiehui-works
2. 点击 **"Add file" → "Upload files"**
3. 依次上传以下文件：
   - `xhs-workflow.html`（新文件）
   - `index.html`（覆盖原文件 ⚠️）
4. 写上 Commit message：`feat: 添加小红书文案生成器工作流`
5. 点击 **"Commit changes"**

### 方法 B：本地 Git 推送

```bash
cd d:\腾讯小龙虾任务
git clone https://github.com/jiang-1223/jiangjiehui-works.git
# 复制文件到仓库
copy xhs-workflow.html jiangjiehui-works\
copy index-new.html jiangjiehui-works\index.html
cd jiangjiehui-works
git add .
git commit -m "feat: 添加小红书文案生成器工作流"
git push origin main
```

---

## 第二步：部署 Cloudflare Worker（代理隐藏 Token）

### 1. 注册/登录 Cloudflare
- 打开 https://dash.cloudflare.com
- 注册或登录账号（免费即可）

### 2. 创建 Worker
1. 左侧菜单 → **Workers & Pages**
2. 点击 **"Create application"**
3. 选择 **"Create Worker"**
4. 名称输入：`coze-proxy`（可以自定义）
5. 点击 **"Deploy"**
6. 然后点击 **"Edit Code"**
7. 删除所有默认代码，粘贴 `coze-proxy-worker.js` 的内容
8. 点击右上角 **"Save and deploy"**

### 3. 获取 Worker URL
- 部署完成后你会看到一个 URL，类似：
  `https://coze-proxy.你的用户名.workers.dev`
- **记录这个 URL！**

### 4. 更新 xhs-workflow.html 中的代理地址
打开 `xhs-workflow.html`，找到这一行（大约在第 190 行）：

```javascript
const PROXY_URL = '/api/proxy';
```

改为你的 Worker URL：

```javascript
const PROXY_URL = 'https://coze-proxy.你的用户名.workers.dev';
```

然后重新上传到 GitHub。

---

## 第三步：验证

上传完成后，Vercel 会自动部署（大约1-2分钟）。

访问以下地址验证：
- 首页：https://jiangjiehui.top
  - 找到「AI工作流 & 自动化」模块，点击「小红书文案生成器」
- 工作流页面：https://jiangjiehui.top/xhs-workflow.html
  - 输入需求，点击「生成文案」测试

---

## ⚠️ 安全提醒

- `coze-proxy-worker.js` 中包含了你的 Coze Token，**不要**把这个文件上传到 GitHub 仓库
- Token 只部署在 Cloudflare Worker 中（服务端），用户无法看到
- 如果 Token 泄露，去扣子平台重新生成即可

---

## 💡 备选方案（不用 Cloudflare）

如果没有 Cloudflare 账号，也可以直接在前端调用（但 Token 会暴露）：

打开 `xhs-workflow.html`，修改以下代码：

```javascript
// 原来的代理方式
const PROXY_URL = 'https://coze-proxy.xxx.workers.dev';
// ...

// 改为直接调用
const COZE_API = 'https://2fd7jvzwph.coze.site/run';
const COZE_TOKEN = '你的Token';
// 修改 fetch 部分...
```

> ⚠️ 这种方式任何人查看网页源码都能看到 Token，仅适合私人/测试使用。
