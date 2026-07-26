import undetected_chromedriver as uc
import time

# 1. 【补丁1】放弃复杂的代理池，直接绑死一个你买的“美国住宅IP”
# 格式: ip:port:user:pass (如果没有，这行删掉，先用本地网络裸奔)
PROXY = "123.45.67.89:8000:user:pass" 

options = uc.ChromeOptions()
if PROXY:
    options.add_argument(f'--proxy-server=http://{PROXY}')

# 2. 【补丁2】换壳防 403 (直接替换你原来的 webdriver.Chrome)
# 这玩意儿在底层抹除了 Selenium 的机器特征，Cloudflare 会以为你是真人
driver = uc.Chrome(options=options)

# ==========================================
# 👇 下面保留你原有的所有代码（打开网页、输入华盛顿号码、点击搜索） 👇
# ==========================================
driver.get("https://www.truepeoplesearch.com/")
# ... 你门手动调几个随机页数放进去 ...
# ... 你的点击搜索逻辑 ...

# 3. 【补丁3】 (加在点击搜索之后)
time.sleep(3)
# 如果 TPS 弹出了 hCaptcha 验证码，脚本不会报错崩溃，而是暂停等你
if "challenge" in driver.page_source or "captcha" in driver.page_source:
    input("⚠️ 触发验证码了！啊昊，请手动在弹出的浏览器里点一下验证码，点完回这里按【回车】让脚本继续跑...")

# ==========================================
# 👇 下面是我给你的补丁 👇
# ==========================================

pip install undetected-chromedriver