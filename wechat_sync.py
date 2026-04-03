# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse
import re
import sys

# 确保输出编码正确
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# IMA 凭证
CLIENT_ID = "67bd8c9ae0c94ae2ff91b35c56d02fe5"

# 读取API key
with open(r"C:\Users\Administrator/.config/ima/api_key", "rb") as f:
    raw = f.read()
    # 尝试不同编码
    for enc in ['utf-8-sig', 'utf-8', 'gbk', 'latin-1']:
        try:
            API_KEY = raw.decode(enc).strip()
            break
        except:
            continue

print(f"CLIENT_ID: {CLIENT_ID[:10]}...")
print(f"API_KEY: {API_KEY[:10]}...")

def ima_api(path, body):
    """调用IMA API"""
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

def get_article_list_from_biz(biz):
    """通过biz获取公众号文章列表"""
    # 这个接口需要特殊的凭证，暂时无法使用
    # 改用其他方法
    return []

# 主流程
print("="*50)
print("开始同步春日泡泡公众号文章到IMA知识库")
print("="*50)

# 1. 列出所有知识库
print("\n[1/4] 获取知识库列表...")
kb_result = ima_api("/openapi/wiki/v1/search_knowledge_base", {
    "query": "",
    "cursor": "",
    "limit": 50
})

if kb_result:
    print(f"成功获取知识库列表")
    print(f"结果: {json.dumps(kb_result, ensure_ascii=False)}")
else:
    print("获取知识库列表失败")

# 2. 搜索春日泡泡
print("\n[2/4] 搜索'春日泡泡'知识库...")
search_result = ima_api("/openapi/wiki/v1/search_knowledge_base", {
    "query": "春日泡泡",
    "cursor": "",
    "limit": 20
})

if search_result:
    print(f"搜索结果: {json.dumps(search_result, ensure_ascii=False, indent=2)}")

# 3. biz参数
print("\n[3/4] 公众号biz参数...")
biz = "MzU0MTM4MzU5Mw=="
print(f"biz: {biz}")

# 4. 导入文章
print("\n[4/4] 准备导入文章...")
print("注意: 需要先在IMA中创建'春日泡泡公众号'知识库")

print("\n" + "="*50)
print("完成!")
