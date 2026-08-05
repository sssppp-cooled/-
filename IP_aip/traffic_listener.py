"""流量监听器 - 从 Burp XML / HAR 提取代理 IP 和 API 端点"""
import json
import re
import base64
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from proxy_pool import ProxyPool


class TrafficListener:
    """流量分析器，返回提取到的 IP 和 API 端点。"""

    IP_RE = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    ID_PARAM_RE = re.compile(
        r'(id|uuid|device_id|user_id|vin|serial)=([^&]+)', re.IGNORECASE)

    def __init__(self):
        self.pool = ProxyPool()
        self.extracted_endpoints = []  # 存储提取到的端点

    def parse_burp_xml(self, xml_path: str) -> list[str]:
        """解析 Burp XML，提取 IP 和 API 端点。

        Returns:
            提取到的 API 端点 URL 列表
        """
        print(f"[*] 解析 Burp XML: {xml_path}")
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except Exception as e:
            print(f"[!] 解析失败: {e}")
            return []

        ip_count = 0
        self.extracted_endpoints = []

        for item in root.findall('item'):
            req_elem = item.find('request')
            if req_elem is None:
                continue
            is_b64 = req_elem.get('base64', 'false').lower() == 'true'
            raw = req_elem.text or ''
            if is_b64:
                try:
                    raw = base64.b64decode(raw).decode('utf-8', errors='ignore')
                except Exception:
                    continue

            host = None
            path = None
            for line in raw.split('\n'):
                if line.lower().startswith('host:'):
                    host = line.split(':', 1)[1].strip().split(':')[0]
                if line.startswith(('GET ', 'POST ', 'PUT ', 'DELETE ', 'PATCH ')):
                    parts = line.split()
                    if len(parts) >= 2:
                        path = parts[1].split('?')[0]

            if host:
                if self.IP_RE.match(host):
                    self.pool.add(host, 80)
                    ip_count += 1
                if path:
                    url = f"https://{host}{path}"
                    self.extracted_endpoints.append(url)

        # 去重
        self.extracted_endpoints = list(set(self.extracted_endpoints))
        print(f"[+] 喂入 {ip_count} 个 IP, 提取 {len(self.extracted_endpoints)} 个端点")
        return self.extracted_endpoints

    def parse_har(self, har_path: str) -> list[str]:
        """解析 HAR 文件，提取 IP 和 API 端点。

        Returns:
            提取到的 API 端点 URL 列表
        """
        print(f"[*] 解析 HAR: {har_path}")
        try:
            with open(har_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"[!] 解析失败: {e}")
            return []

        entries = data.get('log', {}).get('entries', [])
        ip_count = 0
        self.extracted_endpoints = []

        for entry in entries:
            req = entry.get('request', {})
            url = req.get('url', '')
            parsed = urlparse(url)
            host = parsed.netloc.split(':')[0]

            if self.IP_RE.match(host):
                self.pool.add(host, 80)
                ip_count += 1

            if not url.endswith(('.js', '.css', '.png', '.jpg', '.woff')):
                ids = self.ID_PARAM_RE.findall(parsed.query)
                if ids:
                    print(f"  [!] {req.get('method')} {parsed.path} | {ids}")
                self.extracted_endpoints.append(url)

        self.extracted_endpoints = list(set(self.extracted_endpoints))
        print(f"[+] 喂入 {ip_count} 个 IP, 提取 {len(self.extracted_endpoints)} 个端点")
        return self.extracted_endpoints
