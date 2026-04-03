import re
import urllib.request

url = 'https://mp.weixin.qq.com/s/hV23vMzFxiZofBHMVwkSww'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = urllib.request.urlopen(req)
html = response.read().decode('utf-8', errors='ignore')

# 查找biz
patterns = [
    r'biz\s*[=:]\s*["\']([^"\']+)["\']',
    r'__biz\s*[=:]\s*["\']([^"\']+)["\']',
    r'user_name\s*[=:]\s*["\']([^"\']+)["\']',
    r'appuin\s*[=:]\s*["\']([^"\']+)["\']'
]

for p in patterns:
    m = re.search(p, html)
    if m:
        print(f'Found: {m.group(1)}')
        break
else:
    print('No biz found')
