import json
import urllib.request
import urllib.parse
import re

# IMA 凭证
CLIENT_ID = "67bd8c9ae0c94ae2ff91b35c56d02fe5"
API_KEY = open(r"C:\Users\Administrator/.config/ima/api_key", "r").read().strip()

def ima_api(path, body):
    """调用IMA API"""
    url = f"https://ima.qq.com{path}"
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('ima-openapi-clientid', CLIENT_ID)
    req.add_header('ima-openapi-apikey', API_KEY)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"API错误: {e}")
        return None

def get_biz_from_url(url):
    """从文章URL提取biz"""
    # 尝试访问页面提取biz
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            # 多种模式匹配biz
            patterns = [
                r'biz\s*[=:]\s*["\']([A-Za-z0-9+/=]+)["\']',
                r'__biz\s*[=:]\s*["\']([A-Za-z0-9+/=]+)["\']',
                r'"biz"\s*:\s*"([^"]+)"',
                r'var\s+biz\s*=\s*"([^"]+)"',
                r'window\.__biz\s*=\s*"([^"]+)"',
            ]
            
            for p in patterns:
                m = re.search(p, html)
                if m:
                    return m.group(1)
    except Exception as e:
        print(f"获取页面失败: {e}")
    return None

def search_knowledge_base(query=""):
    """搜索知识库"""
    result = ima_api("/openapi/wiki/v1/search_knowledge_base", {
        "query": query,
        "cursor": "",
        "limit": 50
    })
    return result

def get_knowledge_base_info(kb_id):
    """获取知识库详情"""
    result = ima_api("/openapi/wiki/v1/get_knowledge_base", {
        "ids": [kb_id]
    })
    return result

def import_urls(kb_id, urls, folder_id=None):
    """导入URL到知识库"""
    body = {
        "knowledge_base_id": kb_id,
        "urls": urls
    }
    if folder_id:
        body["folder_id"] = folder_id
    
    result = ima_api("/openapi/wiki/v1/import_urls", body)
    return result

# 主流程
print("="*50)
print("开始同步春日泡泡公众号文章到IMA知识库")
print("="*50)

# 1. 搜索或创建知识库
print("\n[1/4] 搜索知识库...")
kb_result = search_knowledge_base("春日泡泡")
print(f"搜索结果: {json.dumps(kb_result, ensure_ascii=False, indent=2)}")

# 2. 如果没找到，列出所有知识库
if not kb_result or not kb_result.get('data', {}).get('info_list'):
    print("\n未找到春日泡泡知识库，列出所有知识库:")
    all_kb = search_knowledge_base("")
    print(json.dumps(all_kb, ensure_ascii=False, indent=2))
else:
    print("\n找到春日泡泡相关知识库!")
    kb_list = kb_result['data']['info_list']
    for kb in kb_list:
        print(f"  - {kb['name']}: {kb['id']}")

# 3. 从文章链接提取biz
print("\n[2/4] 提取公众号biz参数...")
article_url = "https://mp.weixin.qq.com/s/hV23vMzFxiZofBHMVwkSww"
biz = get_biz_from_url(article_url)
if biz:
    print(f"找到biz: {biz}")
else:
    print("未能从页面提取biz，将尝试其他方法")

# 4. 尝试导入文章链接
print("\n[3/4] 导入文章到IMA...")
if kb_result and kb_result.get('data', {}).get('info_list'):
    kb_id = kb_result['data']['info_list'][0]['id']
    result = import_urls(kb_id, [article_url])
    print(f"导入结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
else:
    print("需要先创建知识库或提供知识库ID")

print("\n[4/4] 完成!")
print("="*50)
