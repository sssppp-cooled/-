"""无卡 iPhone 自动化节点 - Appium + WDA + pymobiledevice3

原理:
    iPhone 无 SIM，走 WiFi。把 WiFi HTTP 代理指向静宅，
    则 Safari 请求 = 真 iOS 指纹 + 美国住宅 IP。
    pymobiledevice3 负责装/转发 WDA，Appium 负责驱动。
"""
import subprocess
from appium import webdriver
from appium.options.ios import XCUITestOptions


class IOSNode:
    """单台无卡 iPhone 节点。"""

    def __init__(self, udid: str,
                 wda_url: str = "http://127.0.0.1:8100",
                 appium_url: str = "http://127.0.0.1:4723"):
        self.udid = udid
        self.wda_url = wda_url
        self.appium_url = appium_url

    def setup(self) -> None:
        """用 pymobiledevice3 转发 WDA 端口。"""
        subprocess.run(
            ['python3', '-m', 'pymobiledevice3', 'usbmux',
             'forward', '8100', '8100', '--udid', self.udid],
            capture_output=True)
        print(f"[+] WDA 端口已转发: {self.udid}")

    def open_url(self, url: str) -> webdriver.Remote:
        """驱动 iPhone Safari 打开 URL（请求经手机 WiFi 代理发出）。"""
        options = XCUITestOptions()
        options.platform_name = "iOS"
        options.udid = self.udid
        options.browser_name = "Safari"
        # 复用已跑起的 WDA，Appium 不重新编译
        options.set_capability("webDriverAgentUrl", self.wda_url)

        driver = webdriver.Remote(self.appium_url, options=options)
        driver.get(url)
        print(f"[+] iPhone 已打开: {url}")
        return driver
