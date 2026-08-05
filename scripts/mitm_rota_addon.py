#!/usr/bin/env python3
"""
mitmproxy 实时流量闭环 Addon
═══════════════════════════════════════════════════════════════
【终端启动命令 —— 复制粘贴即可】

    export ROTA_API_URL="http://your-rota-server.com"
    export ROTA_API_KEY="your_secret_key"
    export IPINFO_TOKEN="your_ipinfo_token"  # 可选

    # 场景 A：收集 iOS 访问的 IoT 设备真实 IP（防污染模式）
    export CAPTURE_MODE="target"
    mitmdump -s scripts/mitm_rota_addon.py -p 8080

    # 场景 B：收集/评估上游代理池的出口 IP 质量
    export CAPTURE_MODE="egress"
    mitmdump -s scripts/mitm_rota_addon.py -p 8080

【iPhone 代理设置】
    Wi-Fi → 配置代理 → 手动
    服务器: <运行 mitmdump 的服务器 IP>
    端口: 8080

【功能】
    1. 实时捕获 iOS 设备流量
    2. 双模式切换：target（防污染）/ egress（代理质量评估）
    3. 工业级异常防护：try/except 包裹整个 IP 提取流程
    4. 调用 GeoValidator 验证美国住宅归属
    5. 验证通过的自动推入 Rota 池
═══════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import ipaddress
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mitmproxy import http
from ios_traffic_intel.geo_validator import GeoValidator


# ── 配置 ──
ROTA_API_URL = os.getenv('ROTA_API_URL', 'http://localhost:8000').rstrip('/')
ROTA_API_KEY = os.getenv('ROTA_API_KEY', '')
IPINFO_TOKEN = os.getenv('IPINFO_TOKEN')
ENABLE_GEO_VALIDATION = os.getenv('ENABLE_GEO_VALIDATION', 'true').lower() == 'true'
CAPTURE_MODE = os.getenv('CAPTURE_MODE', 'egress')  # target / egress


class RotaPushAddon:
    def __init__(self):
        self.seen_ips = set()
        self.geo = GeoValidator(ipinfo_token=IPINFO_TOKEN) if ENABLE_GEO_VALIDATION else None
        print(f"[*] RotaPushAddon 已加载 (模式: {CAPTURE_MODE})")
        print(f"[*] Rota API: {ROTA_API_URL}")
        print(f"[*] GeoValidator: {'启用' if self.geo else '禁用'}")

    def request(self, flow: http.HTTPFlow):
        """mitmproxy 在每个请求经过时触发此钩子"""

        # ── 场景 A：收集 iOS 访问的 IoT 设备真实 IP（防污染模式）──
        if CAPTURE_MODE == 'target':
            host = flow.request.host
            try:
                ip_obj = ipaddress.ip_address(host)
                ip_str = str(ip_obj)
            except ValueError:
                return  # request.host 是域名，跳过

        # ── 场景 B：收集上游代理池的出口 IP 质量（默认）──
        else:
            # 工业级异常防护：try/except 包裹整个提取过程
            # 防止 mitmproxy 内部状态异常（DNS 失败、连接 reset、ip_address 为 None）
            try:
                if not flow.server_conn or not flow.server_conn.ip_address:
                    return
                ip_str = flow.server_conn.ip_address[0]
                ip_obj = ipaddress.ip_address(ip_str)
            except (ValueError, IndexError, TypeError, AttributeError):
                return

        # ── 过滤私有/环回/多播 ──
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_multicast:
            return

        # ── 内存去重 ──
        if ip_str in self.seen_ips:
            return
        self.seen_ips.add(ip_str)

        # ── Geo 验证 ──
        if self.geo:
            result = self.geo.verify(ip_str)
            if hasattr(result, 'is_valid_us_residential'):
                is_valid = result.is_valid_us_residential
                confidence = result.confidence
                is_v6 = result.ipv6
                warnings = result.warnings
            else:
                is_valid = result.get('is_valid_us_residential', False)
                confidence = result.get('confidence', 0)
                is_v6 = result.get('ipv6', False)
                warnings = result.get('warnings', [])

            if not is_valid:
                print(f"[-] 拒绝入池: {ip_str} (confidence: {confidence}, {warnings})")
                return
        else:
            confidence = 0
            is_v6 = False

        # ── 推入 Rota ──
        self._push_to_rota(ip_str, confidence, is_v6)

    def _push_to_rota(self, ip: str, confidence: float, is_v6: bool):
        print(f"\n[+] 捕获到新 IP: {ip} (confidence: {confidence:.1f}) -> 推送至 Rota...")

        try:
            headers = {'Authorization': f'Bearer {ROTA_API_KEY}'}
            payload = {
                "ip": ip,
                "port": 80,
                "source": f"mitm_auto_discovery_{CAPTURE_MODE}",
                "tags": {
                    "auto_discovered": "true",
                    "confidence": str(round(confidence, 1)),
                    "ipv6": str(is_v6).lower(),
                    "checked_at": str(int(time.time())),
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
