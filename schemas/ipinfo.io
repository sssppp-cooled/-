import requests
from requests.auth import HTTPProxyAuth
from urllib.parse import quote


username = "your_username"
password = "your_password" # 如果密码有 @ : / 等特殊字符，这样写最安全

# 方式一：使用 HTTPProxyAuth (推荐)
proxy_url = "http://gate.brightdata.com:22225"
proxies = {
    "http": proxy_url,
    "https": proxy_url
}
auth = HTTPProxyAuth(username, password)

try:
    r = requests.get(
        "https://ipinfo.io/json", 
        proxies=proxies, 
        auth=auth,
        timeout=10
    )
    data = r.json()
    print(f"IP: {data.get('ip')}")
    print(f"国家: {data.get('country')}")
    print(f"运营商: {data.get('org')}")
    
    # 简单的自动判断逻辑
    org = data.get('org', '').lower()
    hosting_keywords = ['amazon', 'google', 'digitalocean', 'hetzner', 'ovh', 'vultr', 'cloudflare']
    if any(keyword in org for keyword in hosting_keywords):
        print("⚠️ 警告：检测到数据中心/Hosting IP，极易被 Cloudflare 拦截！")
    else:
        print("✅ 看起来是住宅/ISP IP，质量不错。")

except Exception as e:
    print(f"请求失败: {e}")
