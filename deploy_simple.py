import requests
import base64

# GitHub API 配置
GITHUB_TOKEN = "ghp_fq3KGxslqvXzJzLRZmDQqVHTqVdGmV3lYjHe"
REPO = "jiang-1223/jiangjiehui-works"
FILE_PATH = "xhs-workflow-protected.html"

# 读取本地文件
with open("d:\\腾讯小龙虾任务\\xhs-workflow-protected.html", "r", encoding="utf-8") as f:
    content = f.read()

# API URL
api_url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# 先获取文件 SHA
try:
    response = requests.get(api_url, headers=headers, timeout=10)
    if response.status_code == 200:
        file_data = response.json()
        sha = file_data["sha"]
    else:
        sha = None
except:
    sha = None

# 准备上传数据
data = {
    "message": "fix: 修复扣子API图片参数格式",
    "content": base64.b64encode(content.encode("utf-8")).decode()
}
if sha:
    data["sha"] = sha

# 上传文件
response = requests.put(api_url, headers=headers, json=data, timeout=30)

if response.status_code in [200, 201]:
    print("✅ 文件上传成功！")
    print(f"🔗 https://github.com/{REPO}/blob/main/{FILE_PATH}")
else:
    print(f"❌ 上传失败: {response.status_code}")
    print(response.text)
