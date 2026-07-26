from curl_cffi import requests
from bs4 import BeautifulSoup
import random
import time
import re

# ================= 配置区 =================
# 1. 火锅的华盛顿 202 区号真实号码池 (请替换为你手里的真实号码)
# 建议准备好几百个备料，每次随机抽取，模拟不同居民的查询行为
DC_REAL_NUMBERS = [
    "2025550198", "2025550123", "2025550144", "2025550155", 
    "2025550166", "2025550177", "2025550188", "2025550199"
    # ... 在这里填入你大量的真实号码 ...
]

# 2. TPS 反向电话查找 URL 模板
URL_TEMPLATE = "https://www.truepeoplesearch.com/resultphone?phoneno={}"

# ==========================================

def extract_tps_data(phone_number):
    print(f"\n[*] 正在使用华盛顿真号探测: {phone_number}")
    
    # 核心黑科技：impersonate="chrome120" 
    # 这行代码会让你的 Python 脚本在 Cloudflare 眼里变成真实的 Chrome 120 浏览器
    session = requests.Session(impersonate="chrome120")
    
    headers = {
        "Accept-Language": "en-US,en;q=0.9", # 模拟美国本地用户
        "Referer": "https://www.truepeoplesearch.com/", # 模拟从首页跳转过来的真人行为
    }
    
    url = URL_TEMPLATE.format(phone_number)
    
    try:
        # 发起请求，设置超时
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 403 or "challenge-platform" in response.text:
            print("[-] 警告: 依然被 Cloudflare 拦截！(可能需要配合代理 IP 使用)")
            return False
            
        if response.status_code == 200:
            print(f"[+] 成功绕过 Cloudflare! 状态码: 200")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # --- 开始提取“换号码”得到的数据 ---
            # TPS 的结果通常包含在特定的 div 中，这里提取最核心的“人名”和“关联信息”
            
            # 1. 提取主要目标人物姓名
            name_tags = soup.find_all('h2', class_='name') or soup.find_all('a', href=re.compile(r'/result\?'))
            names = [name.get_text(strip=True) for name in name_tags[:3]] # 取前3个最相关的
            
            # 2. 提取关联地址 (华盛顿本地地址)
            address_tags = soup.find_all('div', class_='address') or soup.find_all('span', string=re.compile(r'Washington|DC|MD|VA'))
            addresses = list(set([addr.get_text(strip=True) for addr in address_tags[:5]]))
            
            # 3. 提取关联的其他电话号码 (这就是你说的“1个换2个/多个”)
            phone_tags = soup.find_all('a', href=re.compile(r'resultphone'))
            related_phones = list(set([p.get_text(strip=True) for p in phone_tags if p.get_text(strip=True) != phone_number]))

            print("\n" + "="*40)
            print(f"🎯 目标号码: {phone_number}")
            print(f"👤 关联姓名: {', '.join(names) if names else '未找到(可能是隐私保护)'}")
            print(f"📍 关联地址: {', '.join(addresses[:3]) if addresses else '无'}")
            print(f"📞 换出的其他号码: {', '.join(related_phones[:3]) if related_phones else '无'}")
            print("="*40 + "\n")
            
            # 将提取的数据保存到你的 CSV 或数据库 (这里用 print 演示)
            return True
        else:
            print(f"[-] 未知状态码: {response.status_code}")
            return False

    except Exception as e:
        print(f"[!] 请求出错: {e}")
        return False

# ================= 执行逻辑 =================
if __name__ == "__main__":
    print("🚀 启动 TPS 华盛顿苹果设备出厂标记 (真人模式)")
    
    # 随机抽取 3 个真实号码进行测试
    test_numbers = random.sample(DC_REAL_NUMBERS, min(3, len(DC_REAL_NUMBERS)))
    
    for num in test_numbers:
        extract_tps_data(num)
        # 🛑 核心反爬策略：真人不可能 1 秒钟查 3 个号码
        # 每次查询后，随机休眠 8 到 15 秒，模拟真人阅读和思考的时间
        sleep_time = random.uniform(8.0, 15.0)
        print(f"⏳ 模拟真人阅读页面，休眠 {sleep_time:.1f} 秒...")
        time.sleep(sleep_time)
