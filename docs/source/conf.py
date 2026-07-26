# 啊昊确保你已安装`curl_cffi`和`beautifulsoup4`（`pip install curl_cffi beautifulsoup4`）TPS极其狡猾。当它检测到你的IP有点可疑但未完全封禁时，不会返回403，而是返回200状态码，并在HTML中塞入”假的关联数据”（如随机生成的假名字、假地址）。
import csv
import random
import time
import re
from curl_cffi import requests
from bs4 import BeautifulSoup

# ================= 配置区 =================
# 你的华盛顿202区号"诱饵"池（请替换为你手里的真实号码）
# 202是华盛顿特区核心区号，TPS对其关联数据的返回率极高
DC_REAL_NUMBERS = [
    "2025550198", "2025550123", "2025550144", 
    "2025550155", "2025550166"
]

# 模拟美国本地真人的请求头
HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.truepeoplesearch.com/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
}

def extract_tps_network(phone):
    """核心解析逻辑：用1个真号，换出它背后的整个关系网"""
    url = f"https://www.truepeoplesearch.com/resultphone?phoneno={phone}"
    
    try:
        # 核心黑科技：impersonate="chrome120"
        # 这行代码在底层重写TLS指纹，让Cloudflare以为你是一个真实的Windows/Mac用户
        res = requests.get(url, headers=HEADERS, impersonate="chrome120", timeout=15)
        
        # 1. 风控检测：如果触发Cloudflare的JS挑战或hCaptcha
        if "challenge-platform" in res.text or "hcaptcha.com" in res.text or res.status_code == 403:
            print(f"[-] 警告: {phone} 触发了验证码/拦截，你的IP已经脏了！")
            return None
            
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 2. 提取核心人物（姓名）
        # TPS的姓名通常藏在带特定href的a标签里
        names = [a.get_text(strip=True) for a in soup.select('a[href*="/result?"]') if a.get_text(strip=True)]
        
        # 3. 提取关联地址（重点抓取DMV地区：DC, Maryland, Virginia）
        addresses = []
        for div in soup.find_all(['div', 'span']):
            text = div.get_text(strip=True)
            if re.search(r'(Washington|DC|Maryland|MD|Virginia|VA)', text, re.IGNORECASE) and len(text) < 100:
                addresses.append(text)
                
        # 4. 提取"1换多"的核心：关联的其他电话号码（Relatives/Associates）
        related_phones = []
        for a in soup.select('a[href*="resultphone"]'):
            p = a.get_text(strip=True)
            # 排除当前查询号码本身
            if p and p != phone and len(p) >= 10:
                related_phones.append(p)
                
        return {
            "target_phone": phone,
            "names": list(set(names))[:3],  # 取前3个最相关的姓名
            "addresses": list(set(addresses))[:2], # 取前2个地址
            "related_phones": list(set(related_phones)) # 这就是你换出的"2个/多个"号码
        }
        
    except Exception as e:
        print(f"[!] 请求出错: {e}")
        return None

# ================= 执行与持久化 =================
if __name__ == "__main__":
    print("🚀 启动TPS华盛顿真号图谱提取器（反Cloudflare模式）")
    
    with open("dc_network_map.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["诱饵号码(202)", "关联姓名", "关联地址(DMV地区)", "换出的其他号码(核心资产)"])
        
        for num in DC_REAL_NUMBERS:
            print(f"\n[*] 正在用真号敲门: {num}")
            data = extract_tps_network(num)
            
            if data:
                writer.writerow([
                    data["target_phone"],
                    " | ".join(data["names"]),
                    " | ".join(data["addresses"]),
                    " | ".join(data["related_phones"])
                ])
                print(f"[+] 成功！换出了 {len(data['related_phones'])} 个关联号码！")
                
            # 🛑 核心反爬策略：真人行为学休眠
            # 机器是0.1秒查一次，真人是查完看一眼，喝口水。
            # 随机休眠15到45秒，极大降低被TPS标记为"扫描器"的概率。
            sleep_time = random.uniform(15.0, 45.0)
            print(f"⏳ 模拟真人阅读页面，休眠 {sleep_time:.1f} 秒...")
            time.sleep(sleep_time)
            
    print("\n✅ 提取完成，数据已保存至dc_network_map.csv")