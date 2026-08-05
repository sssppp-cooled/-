"""ProxyHat 住宅代理集成 - 标准网关协议"""
import uuid
from curl_cffi import requests as cffi_requests


class ProxyHat:
    """ProxyHat 网关，支持国家/会话/TTL 控制。"""

    def __init__(self, host="gate.proxyhat.com", http_port=8080,
                 user_base="d08ba9bawbuoxj", password="YOUR_PASS"):
        self.host = host
        self.port = http_port
        self.user_base = user_base
        self.password = password
        self._domain_sid = {}   # 域名 -> sid（sticky）

    def _username(self, country="us", ttl="10m", sid=None):
        sid = sid or uuid.uuid4().hex[:10]
        return (f"{self.user_base}-country-{country}"
                f"-sid-{sid}-ttl-{ttl}-filter-medium")

    def get_proxy(self, country="us", sticky_domain=None, ttl="10m"):
        """sticky_domain 相同 → 复用 sid → 同 IP。"""
        sid = None
        if sticky_domain:
            sid = self._domain_sid.get(sticky_domain)
        user = self._username(country, ttl, sid)
        if sticky_domain:
            # 记下 sid 以便复用
            self._domain_sid[sticky_domain] = (
                user.split('-sid-')[1].split('-ttl')[0])
        url = f"http://{user}:{self.password}@{self.host}:{self.port}"
        return {'http': url, 'https': url}

    def test(self):
        """验证出口 IP 是否为美国。"""
        p = self.get_proxy()
        r = cffi_requests.get("https://api.ipify.org",
                              proxies=p, impersonate="chrome", timeout=15)
        print(f"[+] 出口 IP: {r.text}")
        return r.text
