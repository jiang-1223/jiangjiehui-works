# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse
import re
import sys
import io

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# IMA凭证
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

BIZ = "MzU0MTM4MzU5Mw=="

print("=" * 50)
print("Chun Ri Pao Pao Gong Zhong Hao Wen Zhang Tong Bu")
print("=" * 50)

PERSONAL_KB_ID = "IsGmcj6AnxQpnZIW4z18ZVy52A_5lw5qN27U7dDVcXc="

print("\n[1/4] Jian Cha Zhi Shi Ku...")
search = ima_api("/openapi/wiki/v1/search_knowledge_base", {
    "query": "Chun Ri Pao Pao",
    "cursor": "",
    "limit": 20
})

kb_id = None
if search and search.get('data', {}).get('info_list'):
    kb_id = search['data']['info_list'][0]['id']
    kb_name = search['data']['info_list'][0]['name']
    print(f"Zhao Dao Zhi Shi Ku: {kb_name}")
else:
    kb_id = PERSONAL_KB_ID
    print("Jiang Shi Yong 'Ge Ren Zhi Shi Ku'")

print("\n[2/4] Gong Zhong Hao Xin Xi...")
print(f"biz: {BIZ}")

print("\n[3/4] Dao Ru Wen Zhang...")

article_urls = [
    "https://mp.weixin.qq.com/s/hV23vMzFxiZofBHMVwkSww"
]

print(f"Zhun Bei Dao Ru {len(article_urls)} Pian Wen Zhang...")

result = ima_api("/openapi/wiki/v1/import_urls", {
    "knowledge_base_id": kb_id,
    "urls": article_urls
})

if result:
    print(f"Dao Ru Jie Guo: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if result.get('code') == 0:
        print("\n[OK] Cheng Gong Dao Ru Wen Zhang!")
    else:
        print(f"\n[FAIL] Dao Ru Shi Bai: {result.get('msg')}")

print("\n[4/4] Wan Cheng!")
print("=" * 50)

print("""
Note:
1. Gong Zhong Hao API Quan Xian Shou Xian, Wu Fa Zi Dong Huo Qu Quan Bu Li Shi Wen Zhang
2. Jian Yi: Zai Gong Zhong Hao Hou Tai Shou Dong Fu Zhi Wen Zhang Lian Jie Fa Gei Wo
3. Wo Ke Yi Bang Zhu Pan Pi Dao Ru
""")
