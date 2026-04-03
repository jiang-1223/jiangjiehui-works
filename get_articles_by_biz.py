# -*- coding: utf-8 -*-
import urllib.request
import re
import json

# 用biz参数直接访问公众号历史页面
biz = 'MzU0MTM4MzU5Mw%3D%3D'  # URL编码的biz
url = f'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz}&scene=124&devicetype=Windows-QQ'

req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

try:
    resp = urllib.request.urlopen(req, timeout=15)
    content = resp.read().decode('utf-8', errors='ignore')
    print('Response length:', len(content))
    
    # 查找appmsg_count（文章总数）
    counts = re.findall(r'appmsg_count["\':\s]+(\d+)', content)
    if counts:
        print('Total articles:', counts[0])
    
    # 查找next_offset
    offsets = re.findall(r'next_offset["\':\s]+(\d+)', content)
    if offsets:
        print('Next offset:', offsets[0])
    
    # 查找文章列表
    # 尝试匹配JSON中的文章数据
    appmsg_list = re.findall(r'"appmsg_list":\s*\[(.*?)\]', content, re.DOTALL)
    if appmsg_list:
        print('Found appmsg_list!')
        for i, item in enumerate(appmsg_list[:1]):
            print('Item:', item[:500])
    
    # 打印关键部分
    if 'history' in content.lower():
        print('Found history section')
        idx = content.lower().find('history')
        print(content[max(0,idx-100):idx+500])
        
except Exception as e:
    print('Error:', str(e))
