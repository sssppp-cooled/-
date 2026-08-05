"""ProxyHat 集成 - HTTP(sticky) + SOCKS5(universal) 双端点"""
import os, re, uuid
from urllib.parse import urlparse
from curl_cffi import requests as cffi_requests


class ProxyHat:
    def __init__(self):
        self.http_url = os.getenv('PROXYHAT_HTTP_URL', '')
        self.socks5_url = os.getenv('PROXYHAT_SOCKS5_URL', '')
        self._domain_sid = {}
        if self.http_url:
            p = urlparse(self.http_url)
            self.user_tpl = p.username
            self.password = p.password
            self.host = p.hostname
            self.port = p.port

    def _set_sid(self, username, sid):
        return re.sub(r'sid-[0-9a-fA-F]+', f'sid-{sid}', username)

    # --- HTTP 端点：sticky 会话 ---
    def http(self, sticky_domain=None) -> dict:
        sid = self._domain_sid.get(sticky_domain) if sticky_domain else None
        sid = sid or uuid.uuid4().hex[:10]
        if sticky_domain:
            self._domain_sid[sticky_domain] = sid
        user = self._set_sid(self.user_tpl, sid)
        url = f"http://{user}:{self.password}@{self.host}:{self.port}"
        return {'http': url, 'https': url}

    # --- SOCKS5 端点：通用轮换 ---
    def socks5(self, remote_dns=True) -> dict:
        scheme = 'socks5h' if remote_dns else 'socks5'
        p = urlparse(self.socks5_url)
        url = f"{scheme}://{p.username}:{p.password}@{p.hostname}:{p.port}"
        return {'http': url, 'https': url}

    def test(self, scheme='http'):
        p = self.http() if scheme == 'http' else self.socks5()
        r = cffi_requests.get("https://api.ipify.org", proxies=p,
                              impersonate="chrome", timeout=15)
        print(f"[+] 出口 IP ({scheme}): {r.text}")
        return r.text
