import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import capsolver
import time
import random

# ================= 配置区 =================
capsolver.api_key = "YOUR_CAPSOLVER_API_KEY" # 填入你的打粉平台 Key
TARGET_PHONE = "2025550198" # 你的华盛顿真号诱饵
TPS_URL = "https://www.truepeoplesearch.com/"
# ==========================================

def bypass_hcaptcha(driver, current_url):
    """核心黑科技：检测 hCaptcha -> 提取 Sitekey -> 调 API -> 注入 Token"""
    
    
    # 1. 提取页面的 sitekey
    try:
        # TPS 的 hCaptcha 通常藏在这个 div 里
        hcaptcha_div = driver.find_element(By.CLASS_NAME, "h-captcha")
        sitekey = hcaptcha_div.get_attribute("data-sitekey")
        print(f"[+] 成功提取 Sitekey: {sitekey}")
    except Exception as e:
        print("[-] 未找到 sitekey，可能页面结构变了")
        return False

    # 2. 调用 CapSolver API (注意：TPS 可能使用的是企业版，需加 enterprise 参数)
    try:
        solution = capsolver.solve({
            "type": "HCaptchaTaskProxyLess",
            "websiteURL": current_url,
            "websiteKey": sitekey,
            # "enterprise": True, # 如果普通版打不过，取消注释这行试试企业版
            "userAgent": driver.execute_script("return navigator.userAgent;") # 保持指纹一致
        })
        token = solution.get("gRecaptchaResponse")
        if not token:
            print("[-] 打码平台未返回有效 Token")
            return False
        print("[+] 打码成功！拿到 Token，准备注入...")
    except Exception as e:
        print(f"[-] 打码 API 调用失败: {e}")
        return False

    # 3. 将 Token 强行注入到页面的隐藏 textarea 中
    inject_js = f"""
        // 找到 hCaptcha 的响应框并塞入 Token
        let textarea = document.querySelector('textarea[name="h-captcha-response"]');
        if(textarea) {{
            textarea.style.display = 'block';
            textarea.value = '{token}';
            textarea.style.display = 'none';
        }}
        // 触发验证成功的回调事件
        if(typeof hcaptcha !== 'undefined') {{
            hcaptcha.getResponse();
        }}
    """
    driver.execute_script(inject_js)
    
    # 4. 模拟真人点击“提交”或“搜索”按钮
    try:
        # 这里需要根据 TPS 实际的提交按钮 class 进行调整
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .search-btn")
        submit_btn.click()
        print("[+] Token 注入并提交成功，等待页面跳转...")
        time.sleep(3)
        return True
    except:
        print("[-] 找不到提交按钮，请手动检查页面结构")
        return False

def main():
    # 1. 启动反指纹浏览器 (核心！)
    options = uc.ChromeOptions()
    # options.add_argument("--headless") # 调试时先别开无头模式，看看它怎么过验证码
    driver = uc.Chrome(options=options)
    
    print(f"[*] 正在访问 TPS 并搜索号码: {TARGET_PHONE}")
    driver.get(TPS_URL)
    time.sleep(random.uniform(2.0, 4.0)) # 模拟真人发呆
    
    # 2. 输入号码并搜索
    try:
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='name']")) # TPS的输入框
        )
        # 模拟真人逐个字符打字
        for char in TARGET_PHONE:
            search_input.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
            
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    except:
        print("[-] 找不到搜索框")
        return

    # 3. 监听是否触发了 hCaptcha (第二道门)
    time.sleep(3)
    current_url = driver.current_url
    
    # 检查页面里是否出现了 hCaptcha 的 iframe
    if "hcaptcha.com" in driver.page_source:
        print("[!] 警告：触发了 TPS 的 hCaptcha 风控！")
        success = bypass_hcaptcha(driver, current_url)
        if not success:
            print("[-] 打码失败，脚本终止")
            return
    else:
        print("[+] 运气不错，或者行为伪装生效，直接进入了结果页！")

    # 4. 解析结果 (这里省略 BeautifulSoup 解析逻辑，和前面一样)
    print("[*] 正在提取关联图谱数据...")
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    # ... 提取姓名、地址、关联号码 ...
    
    input("按回车键退出浏览器...")
    driver.quit()

if __name__ == "__main__":
    main()


  