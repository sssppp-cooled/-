base_dir = "/mnt/agents/output/ios-traffic-intel"

# 直接创建/覆盖 mitm_rota_addon.py，包含运行命令提醒
addon_code = '''#!/usr/bin/env python3
"""
mitmproxy 实时流量闭环 Addon
═══════════════════════════════════════════════════════════════
【终端启动命令 —— 复制粘贴即可】

    export ROTA_API_URL="http://your-rota-server.com"
    export ROTA_API_KEY="your_secret_key"

    mitmdump -s scripts/mitm_rota_addon.py -p 8080

【iPhone 代理设置】
    Wi-Fi → 配置代理 → 手动
    服务器: <运行 mitmdump 的服务器 IP>
    端口: 8080

功能:
    1. 实时捕获 iOS 设备流量
    2. 提取出口 IP（不是目标域名）
    3. 调用 GeoValidator 验证美国住宅归属
    4. 验证通过的自动推入 Rota 池
    5. 内存去重，避免重复推送

环境变量:
    ROTA_API_URL    — Rota API 地址（默认 http://localhost:8000）
    ROTA_API_KEY    — Rota JWT Token（必填）
    IPINFO_TOKEN    — IPinfo API Token（可选，用于 Geo 验证）
═══════════════════════════════════════════════════════════════
"""

import os
import sys
import ipaddress
import requests
from pathlib import Path

# 把项目根目录加入路径，以便导入 GeoValidator
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mitmproxy import http
from ios_traffic_intel.geo_validator import GeoValidator


# ── 配置 ──
ROTA_API_URL = os.getenv(\'ROTA_API_URL\', \'http://localhost:8000\').rstrip(\'/\')
ROTA_API_KEY = os.getenv(\'ROTA_API_KEY\', \'\')
IPINFO_TOKEN = os.getenv(\'IPINFO_TOKEN\')
ENABLE_GEO_VALIDATION = os.getenv(\'ENABLE_GEO_VALIDATION\', \'true\').lower() == \'true\'


class RotaPushAddon:
    def __init__(self):
        self.seen_ips = set()
        self.geo = GeoValidator(ipinfo_token=IPINFO_TOKEN) if ENABLE_GEO_VALIDATION else None
        print(f"[*] RotaPushAddon 已加载")
        print(f"[*] Rota API: {ROTA_API_URL}")
        print(f"[*] GeoValidator: {\'启用\' if self.geo else \'禁用\'}")

    def request(self, flow: http.HTTPFlow):
        """mitmproxy 在每个请求经过时触发此钩子"""
        if not flow.server_conn or not flow.server_conn.ip_address:
            return

        ip_str = flow.server_conn.ip_address[0]

        try:
            ip_obj = ipaddress.ip_address(ip_str)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_multicast:
                return
        except ValueError:
            return

        if ip_str in self.seen_ips:
            return
        self.seen_ips.add(ip_str)

        if self.geo:
            result = self.geo.verify(ip_str)
            if not result.is_valid_us_residential:
                print(f"[-] 拒绝入池: {ip_str} (confidence: {result.confidence}, {result.warnings})")
                return
            confidence = result.confidence
            is_v6 = result.ipv6
        else:
            confidence = 0
            is_v6 = False

        self._push_to_rota(ip_str, confidence, is_v6)

    def _push_to_rota(self, ip: str, confidence: float, is_v6: bool):
        print(f"\\n[+] 捕获到新出口 IP: {ip} (confidence: {confidence:.1f}) -> 推送至 Rota...")

        try:
            headers = {\'Authorization\': f\'Bearer {ROTA_API_KEY}\'}
            payload = {
                "ip": ip,
                "port": 80,
                "source": "mitm_auto_discovery",
                "tags": {
                    "auto_discovered": "true",
                    "confidence": str(round(confidence, 1)),
                    "ipv6": str(is_v6).lower(),
                    "checked_at": str(int(__import__(\'time\').time())),
                }
            }

            resp = requests.post(
                f"{ROTA_API_URL}/api/v1/proxies",
                json=payload,
                headers=headers,
                timeout=5
            )

            if resp.status_code in (200, 201):
                print(f"    [✓] 已入库")
            else:
                print(f"    [✗] Rota 返回 {resp.status_code}: {resp.text[:100]}")

        except Exception as e:
            print(f"    [✗] 推送失败: {e}")


# mitmproxy 加载入口
addons = [RotaPushAddon()]
'''

with open(f"{base_dir}/scripts/mitm_rota_addon.py", "w", encoding="utf-8") as f:
    f.write(addon_code)

print("已创建 scripts/mitm_rota_addon.py")
print("=" * 50)

# 验证前 30 行
with open(f"{base_dir}/scripts/mitm_rota_addon.py", "r", encoding="utf-8") as f:
    lines = f.readlines()[:30]
    for i, line in enumerate(lines, 1):
        print(f"{i:2d} | {line.rstrip()}")
