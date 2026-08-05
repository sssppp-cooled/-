#!/usr/bin/env python3
"""
mitmproxy 上游代理入口轮换器
═══════════════════════════════════════════════════════════════
【功能】
    iPhone → mitmproxy (本机:8080) → 静宅/ProxyHat 入口 IP → 目标网站
    同时 mitmproxy 捕获流量，供 ios-traffic-intel 分析

【终端启动命令】
    # 单用轮换器
    mitmdump -s scripts/mitm_proxy_rotator.py -p 8080

    # 轮换器 + Rota 推送（多 addon 同时加载）
    mitmdump -s scripts/mitm_proxy_rotator.py -s scripts/mitm_rota_addon.py -p 8080

【配置方式】
    1. 环境变量: export PROXY_ENTRIES='us1.proxyhat.io:8080,user,pass|us2.proxyhat.io:8080,user,pass'
    2. 或修改本文件底部的 entries 列表

【热重载】
    修改本文件保存后，mitmproxy 自动重新加载，无需重启
═══════════════════════════════════════════════════════════════
"""

import os
import base64
import random
from mitmproxy import http


class ProxyEntryRotator:
    """
    动态轮换上游代理入口（静宅/ProxyHat/Oxylabs 等）
    
    支持两种模式:
        round-robin: 顺序轮换（默认）
        random:      随机选择
        sticky:      同一 host 保持同一入口（会话保持）
    """

    def __init__(self):
        self.entries = self._load_entries()
        self.mode = os.getenv('PROXY_ROTATE_MODE', 'round-robin')  # round-robin / random / sticky
        self.rotate_after = int(os.getenv('PROXY_ROTATE_AFTER', '10'))  # 每 N 请求轮换
        self.sticky_ttl = int(os.getenv('PROXY_STICKY_TTL', '30'))    # sticky 模式保持秒数
        
        self.current_index = 0
        self.request_count = 0
        self.sticky_map = {}  # host -> (entry_index, timestamp)
        
        print(f"[*] ProxyEntryRotator 已加载")
        print(f"[*] 模式: {self.mode}, 入口数: {len(self.entries)}, 每 {self.rotate_after} 请求轮换")

    def _load_entries(self):
        """从环境变量或硬编码加载代理入口"""
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
        
        # 默认硬编码（修改这里适配你的静宅/ProxyHat）
        return [
            # {"host": "us1.proxyhat.io", "port": 8080, "user": "your_user", "pass": "your_pass"},
            # {"host": "us2.proxyhat.io", "port": 8080, "user": "your_user", "pass": "your_pass"},
        ]

    def http_connect(self, flow: http.HTTPFlow):
        """
        HTTPS CONNECT 隧道处理
        把 CONNECT 目标从真实网站改为代理入口
        """
        if not self.entries:
            return
        
        entry = self._select_entry(flow.request.host)
        
        # 修改 CONNECT 目标到代理入口
        flow.request.host = entry["host"]
        flow.request.port = entry["port"]
        
        # 添加代理认证头
        if entry["user"]:
            creds = base64.b64encode(f"{entry['user']}:{entry['pass']}".encode()).decode()
            flow.request.headers["Proxy-Authorization"] = f"Basic {creds}"
        
        print(f"[Rotator] CONNECT {flow.request.host}:{flow.request.port} → via {entry['host']}:{entry['port']}")

    def request(self, flow: http.HTTPFlow):
        """
        HTTP 请求处理（非 CONNECT）
        """
        if not self.entries or flow.request.scheme == "https":
            return  # HTTPS 走 http_connect
        
        entry = self._select_entry(flow.request.host)
        flow.request.host = entry["host"]
        flow.request.port = entry["port"]
        
        if entry["user"]:
            creds = base64.b64encode(f"{entry['user']}:{entry['pass']}".encode()).decode()
            flow.request.headers["Proxy-Authorization"] = f"Basic {creds}"

    def _select_entry(self, target_host: str):
        """根据模式选择入口"""
        import time
        
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
        entry = self.entries[self.current_index]
        print(f"[Rotator] ▶ 切换到入口: {entry['host']}:{entry['port']}")


# mitmproxy 加载入口
addons = [ProxyEntryRotator()]
