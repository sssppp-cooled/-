import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class Proxy:
    host: str
    port: int
    username: str
    password: str
    protocol: str = "http"
    country: str = "US"
    proxy_type: str = "residential"
    
    fail_count: int = 0
    last_used: Optional[datetime] = None
    last_fail: Optional[datetime] = None
    total_requests: int = 0
    success_rate: float = 1.0
    
    @property
    def url(self) -> str:
        return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
    
    def mark_success(self):
        self.total_requests += 1
        self.last_used = datetime.now()
        self.fail_count = max(0, self.fail_count - 1)
        self.success_rate = (self.success_rate * (self.total_requests - 1) + 1) / self.total_requests
    
    def mark_fail(self):
        self.total_requests += 1
        self.fail_count += 1
        self.last_fail = datetime.now()
        self.success_rate = (self.success_rate * (self.total_requests - 1)) / self.total_requests


class ProxyPool:
    def __init__(self, proxy_list: List[Proxy], max_fail: int = 3, cooldown_minutes: int = 30):
        self.proxies = proxy_list
        self.max_fail = max_fail
        self.cooldown = timedelta(minutes=cooldown_minutes)
        self._blacklist = set()
    
    @classmethod
    def from_json(cls, filepath: str, max_fail: int = 3, cooldown_minutes: int = 30):
        with open(filepath, 'r') as f:
            data = json.load(f)
        proxies = [
            Proxy(
                host=p['host'], port=p['port'],
                username=p['user'], password=p['pass'],
                country=p.get('country', 'US'),
                proxy_type=p.get('type', 'residential')
            ) for p in data
        ]
        return cls(proxies, max_fail, cooldown_minutes)
    
    def get_proxy(self) -> Proxy:
        available = [
            p for p in self.proxies 
            if p.fail_count < self.max_fail 
            and (p.last_fail is None or datetime.now() - p.last_fail > self.cooldown)
            and p not in self._blacklist
        ]
        
        if not available:
            self._blacklist.clear()
            available = sorted(self.proxies, key=lambda x: x.fail_count)[:max(1, len(self.proxies)//5)]
        
        weights = [p.success_rate ** 3 for p in available]
        total = sum(weights) or 1
        probs = [w / total for w in weights]
        chosen = random.choices(available, weights=probs, k=1)[0]
        chosen.last_used = datetime.now()
        return chosen
    
    def report(self, proxy: Proxy, success: bool):
        if success:
            proxy.mark_success()
        else:
            proxy.mark_fail()
            if proxy.fail_count >= self.max_fail:
                self._blacklist.add(proxy)
                print(f"⚠️ 代理熔断: {proxy.host}")
