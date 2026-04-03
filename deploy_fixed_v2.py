import requests
import base64

# GitHub API 配置
GITHUB_TOKEN = "ghp_fq3KGxslqvXzJzLRZmDQqVHTqVdGmV3lYjHe"
REPO = "jiang-1223/jiangjiehui-works"
FILE_PATH = "xhs-workflow-protected.html"

# 读取本地文件
with open("d:\\腾讯小龙虾任务\\xhs-workflow-protected.html", "r", encoding="utf-8") as f:
    content = f.read()

# 先获取文件 SHA（用于更新）
api_url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# 检查文件是否存在
response = requests.get(api_url, headers=headers)

if response.status_code == 200:
    # 文件存在，需要获取 SHA
    file_data = response.json()
    sha = file_data["sha"]
    method = "PUT"
    data = {
        "message": "fix: 修复扣子API图片参数格式，按照官方文档调整",
        "content": base64.b64encode(content.encode("utf-8")).decode(),
        "sha": sha
    }
elif response.status_code == 404:
    # 文件不存在，直接创建
    method = "PUT"
    data = {
        "message": "fix: 修复扣子API图片参数格式，按照官方文档调整",
        "content": base64.b64encode(content.encode("utf-8")).decode()
    }
else:
    print(f"检查文件失败: {response.status_code} - {response.text}")
    exit(1)

# 上传文件
response = requests.put(api_url, headers=headers, json=data)

if response.status_code in [200, 201]:
    print("✅ 文件上传成功！")
    print(f"📁 文件路径: {FILE_PATH}")
    print(f"🔗 查看: https://github.com/{REPO}/blob/main/{FILE_PATH}")
else:
    print(f"❌ 上传失败: {response.status_code}")
    print(response.text)
