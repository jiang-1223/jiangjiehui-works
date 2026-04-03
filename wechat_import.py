# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse
import re
import sys

# IMA 凭证
CLIENT_ID = "67bd8c9ae0c94ae2ff91b35c56d02fe5"

with open(r"C:\Users\Administrator/.config/ima/api_key", "rb") as f:
    raw = f.read()
    for enc in ['utf-8-sig', 'utf-8', 'gbk', 'latin-1']:
        try:
            API_KEY = raw.decode(enc).strip()
            break
        except:
            continue

def ima_api(path, body):
    url = f"https://ima.qq.com{path}"
    data = json.dumps(body, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('ima-openapi-clientid', CLIENT_ID)
    req.add_header('ima-openapi-apikey', API_KEY)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"API错误: {e}")
        return None

# 公众号biz
BIZ = "MzU0MTM4MzU5Mw=="

print("="*50)
print("春日泡泡公众号文章同步")
print("="*50)

# 1. 查找或确定知识库
# 已知"个人知识库"的ID
PERSONAL_KB_ID = "IsGmcj6AnxQpnZIW4z18ZVy52A_5lw5qN27U7dDVcXc="

# 检查"春日泡泡"是否已存在
print("\n[1/4] 检查知识库...")
search = ima_api("/openapi/wiki/v1/search_knowledge_base", {
    "query": "春日泡泡",
    "cursor": "",
    "limit": 20
})

kb_id = None
if search and search.get('data', {}).get('info_list'):
    kb_id = search['data']['info_list'][0]['id']
    kb_name = search['data']['info_list'][0]['name']
    print(f"找到知识库: {kb_name}")
else:
    # 使用"个人知识库"
    kb_id = PERSONAL_KB_ID
    print("将使用'个人知识库'作为存储位置")
    print("如需创建专属知识库，请在IMA中手动创建'春日泡泡公众号'知识库")

# 2. 获取文章链接列表
# 这里我们只能获取到用户提供的文章链接
# 公众号的完整文章列表需要特殊的API权限

print("\n[2/4] 公众号信息...")
print(f"biz: {BIZ}")
print("注意: 获取完整历史文章需要公众号具备相应API权限")

# 3. 导入文章链接
print("\n[3/4] 导入文章...")

# 用户提供的文章链接
article_urls = [
    "https://mp.weixin.qq.com/s/hV23vMzFxiZofBHMVwkSww"
]

print(f"准备导入 {len(article_urls)} 篇文章...")

result = ima_api("/openapi/wiki/v1/import_urls", {
    "knowledge_base_id": kb_id,
    "urls": article_urls
})

if result:
    print(f"导入结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result.get('code') == 0:
        print("\n✅ 成功导入文章!")
    else:
        print(f"\n❌ 导入失败: {result.get('msg')}")

# 4. 完成
print("\n[4/4] 完成!")
print("="*50)

print("""
📝 后续步骤:

由于公众号API权限限制，无法自动获取全部历史文章。

可选方案:
1. 【推荐】在公众号后台手动复制文章链接发给我，
   我帮你逐批导入

2. 使用第三方工具(如新榜)导出文章链接列表，
   然后发给我批量导入

3. 在IMA桌面端手动添加文章链接

请告诉我你想用哪种方式~
""")
