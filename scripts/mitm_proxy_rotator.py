#!/usr/bin/env python3
"""
mitmproxy 动态上游代理轮换器 (修正版)
═══════════════════════════════════════════════════════════════
【修正说明】
    使用 flow.server_conn.address 替代修改 request.host，
    完美解决 HTTPS SNI 校验失败和 HTTP Host 头错误的问题。
═══════════════════════════════════════════════════════════════
"""

import os
import base64
import random
import time
from mitmproxy import http

class ProxyEntryRotator:
    def __init__(self):
        self.entries = self._load_entries()
        self.mode = os.getenv('PROXY_ROTATE_MODE', 'round-robin')
        self.rotate_after = int(os.getenv('PROXY_ROTATE_AFTER', '10'))
        self.sticky_ttl = int(os.getenv('PROXY_STICKY_TTL', '30'))
        
        self.current_index = 0
        self.request_count = 0
        self.sticky_map = {}
        
        print(f"[*] ProxyEntryRotator 已加载 (官方 API 版)")
        print(f"[*] 模式: {self.mode} | 入口数: {len(self.entries)} | 轮换频率: {self.rotate_after}")

    def _load_entries(self):
        env = os.getenv('PROXY_ENTRIES', '')
        if env:
            entries = []
            for segment in env.split('|'):
                parts = segment.split(',')
                if len(parts) >= 2:
                    host_port = parts[0].split(':')
                    entries.append({
                        "host": host_port[0],
                        "port": int(host_port[1]) if len(host_port) > 1 else 8080,
                        "user": parts[1] if len(parts) > 1 else "",
                        "pass": parts[2] if len(parts) > 2 else "",
                    })
            return entries
        return []

    def _select_entry(self, target_host: str):
        if not self.entries:
            return None
            
        if self.mode == "random":
            return random.choice(self.entries)
        
        elif self.mode == "sticky":
            now = time.time()
            if target_host in self.sticky_map:
                idx, ts = self.sticky_map[target_host]
                if now - ts < self.sticky_ttl:
                    return self.entries[idx]
            
            idx = self.current_index
            self.sticky_map[target_host] = (idx, now)
            self._rotate()
            return self.entries[idx]
        
        else:  # round-robin
            self.request_count += 1
            if self.request_count >= self.rotate_after:
                self._rotate()
            return self.entries[self.current_index]

    def _rotate(self):
        self.current_index = (self.current_index + 1) % len(self.entries)
        self.request_count = 0

    def _apply_proxy(self, flow: http.HTTPFlow, entry: dict):
        """核心修正：使用 server_conn.address 设置上游代理 [[19]]"""
        # 1. 告诉 mitmproxy 底层连接到这个代理 IP
        flow.server_conn.address = (entry["host"], entry["port"])
        
        # 2. 注入代理认证头 (mitmproxy 会自动将其传递给上游代理) [[15]]
        if entry["user"]:
            creds = base64.b64encode(f"{entry['user']}:{entry['pass']}".encode()).decode()
            flow.request.headers["Proxy-Authorization"] = f"Basic {creds}"

    def http_connect(self, flow: http.HTTPFlow):
        """处理 HTTPS CONNECT 隧道"""
        entry = self._select_entry(flow.request.host)
        if entry:
            self._apply_proxy(flow, entry)
            # 打印日志时不修改 flow.request.host，保持原始目标可见
            print(f"[Rotator] HTTPS {flow.request.host} -> via {entry['host']}:{entry['port']}")

    def request(self, flow: http.HTTPFlow):
        """处理普通 HTTP 请求"""
        if flow.request.scheme == "https":
            return  # HTTPS 已经在 http_connect 处理过了
            
        entry = self._select_entry(flow.request.host)
        if entry:
            self._apply_proxy(flow, entry)
            print(f"[Rotator] HTTP  {flow.request.host} -> via {entry['host']}:{entry['port']}")

addons = [ProxyEntryRotator()]
