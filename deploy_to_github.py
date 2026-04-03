#!/usr/bin/env python3
"""上传 xhs-workflow-protected.html 到 GitHub"""

import base64
import json
import urllib.request
import urllib.error

# GitHub 配置
GITHUB_TOKEN = 'ghp_xK9XqVRz1vD1mL2yPqA8nP4jR6tE3gH5sB7cD8'  # 你的 token
REPO_OWNER = 'jiang-1223'
REPO_NAME = 'jiangjiehui-works'
FILE_PATH = 'xhs-workflow-protected.html'
BRANCH = 'master'

def main():
    # 读取本地文件
    with open(r'd:\腾讯小龙虾任务\xhs-workflow-protected.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 文件内容 Base64 编码
    file_content = base64.b64encode(content.encode('utf-8')).decode('ascii')

    # API URL
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'

    # 先获取当前文件 SHA（如果存在）
    sha = None
    req = urllib.request.Request(url, headers={
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    })
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            sha = data.get('sha')
            print(f'当前文件存在，SHA: {sha}')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print('文件不存在，将创建新文件')
        else:
            print(f'获取文件信息失败: {e.code}')
            raise

    # 上传文件
    data = {
        'message': 'feat: 添加小红书工作流页面 (Coze Web SDK)',
        'content': file_content,
        'branch': BRANCH
    }
    if sha:
        data['sha'] = sha  # 如果文件存在，需要提供 SHA

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        },
        method='PUT'
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f'✅ 上传成功！')
            print(f'文件地址: {result["content"]["html_url"]}')
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f'❌ 上传失败: {e.code}')
        print(f'错误详情: {error_body}')
        raise

if __name__ == '__main__':
    main()
