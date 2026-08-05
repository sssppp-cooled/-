#!/usr/bin/env python3
"""
TrafficAnalyzer — iOS 流量情报分析器
═══════════════════════════════════════════════════════════════
职责边界（与 Rota / go-ios 明确分工）:
    ✅ 本模块: HAR/mitmproxy 解析、API 端点提取、IDOR/BOLA 检测
    ❌ Rota:   代理池管理、健康检查、IP 轮换、GeoIP
    ❌ go-ios: iOS 设备控制、WDA 部署、USB 隧道
═══════════════════════════════════════════════════════════════
"""

import json
import re
from urllib.parse import urlparse, parse_qsl
from typing import List, Dict, Set, Optional, Any
from pathlib import Path

from .models import APIEndpoint, TrafficReport


class TrafficAnalyzer:
    IDOR_PATTERNS: List[str] = [
        r'(?:^|&)(id|uuid|device_id|user_id|account_id|order_id|transaction_id|session_id|player_id|customer_id|member_id)=([^&]+)',
        r'/(?:users?|orders?|accounts?|devices?|customers?|members?|players?|items?|products?)/([0-9]+|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})',
        r'\b(userId|playerId|accountId|orderId)\s*[:=]\s*["\']?([^"\'\s,}]+)',
    ]

    STATIC_EXTENSIONS: Set[str] = {
        '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg',
        '.woff', '.woff2', '.ttf', '.eot', '.ico', '.mp4', '.webp',
        '.map', '.json', '.xml', '.txt', '.log',
    }

    NOISE_HOSTS: Set[str] = {
        'firebaseinstallations.googleapis.com',
        'app-measurement.com',
        'google-analytics.com',
        'analytics.google.com',
        'crashlytics.com',
        'reports.crashlytics.com',
        'appsflyer.com',
        'sdk.appsflyer.com',
        'events.appsflyer.com',
        'adjust.com',
        'app.adjust.com',
        'onesignal.com',
        'api.onesignal.com',
        'facebook.com',
        'graph.facebook.com',
        'doubleclick.net',
        'googleads.g.doubleclick.net',
        'googlesyndication.com',
        'googleusercontent.com',
        'firebaselogging.googleapis.com',
        'mobileanalytics.*.amazonaws.com',
        'metrics.*.amazonaws.com',
    }

    HEALTH_PATTERNS: Set[str] = {
        '/health', '/healthz', '/ping', '/ready',
        '/alive', '/status', '/liveness', '/readiness',
        '/_health', '/_ping', '/api/health',
    }

    def __init__(self):
        self.idor_regex = re.compile('|'.join(f'({p})' for p in self.IDOR_PATTERNS), re.IGNORECASE)
        self.ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        self.discovered_apis: List[APIEndpoint] = []
        self.unique_endpoints: Set[str] = set()

    def parse_har(self, har_path: str, goios_udids: Optional[List[str]] = None) -> TrafficReport:
        path = Path(har_path)
        if not path.exists():
            raise FileNotFoundError(f"HAR 文件不存在: {har_path}")

        print(f"[*] 解析 HAR: {har_path}")

        with open(har_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        entries = data.get('log', {}).get('entries', [])
        results: List[APIEndpoint] = []

        for entry in entries:
            api = self._parse_entry(entry)
            if api:
                results.append(api)

        report = TrafficReport(
            source_file=str(path.resolve()),
            total_entries=len(entries),
            unique_apis=len(results),
            idor_targets=len([e for e in results if e.idor_params]),
            endpoints=results,
            goios_devices=goios_udids or [],
        )

        print(report.summary())
        return report

    def _parse_entry(self, entry: Dict[str, Any]) -> Optional[APIEndpoint]:
        request = entry.get('request', {})
        response = entry.get('response', {})

        method = request.get('method', 'GET')
        url = request.get('url', '')
        parsed = urlparse(url)
        host = parsed.netloc.split(':')[0].lower()
        path = parsed.path
        query = parsed.query

        if not host:
            return None
        if any(noise in host for noise in self.NOISE_HOSTS):
            return None
        if any(path.endswith(ext) for ext in self.STATIC_EXTENSIONS):
            return None
        if any(path.endswith(p) for p in self.HEALTH_PATTERNS):
            return None

        sig = f"{method}:{host}:{path}"
        if sig in self.unique_endpoints:
            return None
        self.unique_endpoints.add(sig)

        query_params = parse_qsl(query) if query else []
        source_ip = self._extract_source_ip(request.get('headers', []))
        headers = {h.get('name', ''): h.get('value', '') for h in request.get('headers', [])}
        idor_params = self._detect_idor(query, path)

        api = APIEndpoint(
            method=method,
            host=host,
            path=path,
            scheme=parsed.scheme or "https",
            query_params=query_params,
            idor_params=idor_params,
            headers=headers,
            request_body=request.get('postData', {}).get('text'),
            response_status=response.get('status', 0),
            response_size=response.get('bodySize', 0),
            timestamp=entry.get('startedDateTime'),
            source_ip=source_ip,
            tags=self._auto_tag(path, headers, idor_params),
        )

        risk = "🔴" if api.is_high_risk else ("🟡" if api.idor_params else "🟢")
        print(f"  {risk} {method} {host}{path}")
        if api.idor_params:
            print(f"     └─ IDOR: {api.idor_params}")

        return api

    def _extract_source_ip(self, headers: List[Dict[str, str]]) -> Optional[str]:
        for header in headers:
            name = header.get('name', '').lower()
            if name in ('x-forwarded-for', 'x-real-ip', 'x-client-ip'):
                ip = header.get('value', '').split(',')[0].strip()
                if self.ip_pattern.match(ip):
                    return ip
        return None

    def _detect_idor(self, query: str, path: str) -> List[tuple]:
        found = []
        for match in self.idor_regex.finditer(f"?{query}"):
            groups = [g for g in match.groups() if g is not None]
            if len(groups) >= 2:
                found.append((groups[0], groups[1]))

        path_match = re.search(
            r'/(?:users?|orders?|accounts?|devices?|customers?|members?|players?|items?|products?|admin)/([0-9]+|[0-9a-fA-F-]{36})',
            path, re.I
        )
        if path_match:
            found.append(('path_id', path_match.group(1)))

        return found

    def _auto_tag(self, path: str, headers: Dict[str, str], idor: List[tuple]) -> List[str]:
        tags = []
        if idor:
            tags.append('idor')
        if 'admin' in path.lower():
            tags.append('admin')
        if 'api' in path.lower():
            tags.append('api')
        if headers.get('Authorization') or headers.get('authorization'):
            tags.append('auth')
        if 'graphql' in path.lower():
            tags.append('graphql')
        return tags

    def export_nuclei_targets(self, endpoints: List[APIEndpoint], output_path: str,
                               filter_tag: Optional[str] = None) -> int:
        filtered = endpoints
        if filter_tag:
            filtered = [e for e in endpoints if filter_tag in e.tags]

        lines = [e.to_nuclei_line() for e in filtered]
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines) + "\n")

        print(f"[+] 导出 {len(lines)} 个目标 → {output_path}")
        return len(lines)

    def export_idor_targets(self, report: TrafficReport, output_path: str) -> int:
        idor = [e for e in report.endpoints if e.idor_params]
        return self.export_nuclei_targets(idor, output_path)

    def export_rota_source_ips(self, report: TrafficReport, output_path: str) -> int:
        ips = sorted(set(
            e.source_ip for e in report.endpoints
            if e.source_ip and self.ip_pattern.match(e.source_ip)
        ))
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(ips) + "\n")
        print(f"[+] 导出 {len(ips)} 个源 IP → {output_path}")
        return len(ips)
