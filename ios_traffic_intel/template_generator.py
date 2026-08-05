#!/usr/bin/env python3
"""
NucleiTemplateGenerator — 从流量情报自动生成检测模板
═══════════════════════════════════════════════════════════════
把 TrafficAnalyzer 提取的 API 端点，自动转换成 Nuclei YAML 模板。
充分利用 Extractors（regex / json / kval / dsl / xpath）提取动态数据。
═══════════════════════════════════════════════════════════════
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Any

from .models import APIEndpoint


class TemplateGenerator:
    """
    根据 API 端点特征自动生成 Nuclei 检测模板。
    """

    def __init__(self, author: str = "ios-traffic-intel", severity: str = "high"):
        self.author = author
        self.severity = severity
        self.generated: List[str] = []

    def from_endpoints(self, endpoints: List[APIEndpoint], output_dir: str) -> List[str]:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        files: List[str] = []

        for i, api in enumerate(endpoints):
            if not api.is_high_risk and not api.idor_params:
                continue

            template = self._build_template(api, index=i)
            if not template:
                continue

            filename = self._sanitize_filename(api)
            filepath = out / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template)
            files.append(str(filepath))
            print(f"  [+] 生成模板: {filepath.name}")

        print(f"[*] 共生成 {len(files)} 个 Nuclei 模板 → {out}")
        return files

    def _build_template(self, api: APIEndpoint, index: int) -> Optional[str]:
        if api.idor_params:
            return self._bola_template(api, index)
        if 'graphql' in api.tags:
            return self._graphql_template(api, index)
        if 'admin' in api.tags:
            return self._admin_bypass_template(api, index)
        return None

    def _bola_template(self, api: APIEndpoint, index: int) -> str:
        resource_match = re.search(r'/([a-z]+)/[0-9a-f-]+', api.path, re.I)
        resource = resource_match.group(1) if resource_match else "resource"
        victim_path = re.sub(r'/[0-9a-fA-F-]{36}', '/11111111-1111-1111-1111-111111111111', api.path)
        victim_path = re.sub(r'/[0-9]+', '/999999', victim_path, count=1)

        return f"""id: ios-bola-{resource.lower()}-{index:03d}

info:
  name: iOS API BOLA - {resource} IDOR
  author: {self.author}
  severity: {self.severity}
  description: |
    Detects Broken Object Level Authorization in {resource} endpoint.
    Original path: {api.path}
    IDOR params: {api.idor_params}
  tags: ios,mobile,bola,idor,{resource.lower()}

http:
  - raw:
      - |+
        {api.method} {api.path} HTTP/1.1
        Host: {{{{Hostname}}}}
        User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)
        Accept: application/json
        {self._format_headers(api.headers)}

    matchers:
      - type: status
        status:
          - 200

    extractors:
      - type: dsl
        name: legit_size
        dsl:
          - "len(body)"
        internal: true

  - raw:
      - |+
        {api.method} {victim_path} HTTP/1.1
        Host: {{{{Hostname}}}}
        User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)
        Accept: application/json
        {self._format_headers(api.headers)}

    matchers-condition: and
    matchers:
      - type: status
        status:
          - 200
      - type: dsl
        dsl:
          - "status_code == 200"
          - "len(body) > 100"
          - '!contains(body, \\"Unauthorized\\")'
          - '!contains(body, \\"401\\")'

    extractors:
      - type: json
        name: leaked_data
        json:
          - '.data'
          - '.user'
          - '.email'
        part: body

      - type: regex
        name: email_leak
        part: body
        group: 1
        regex:
          - '([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\\\.[a-zA-Z]{{2,}})'

      - type: kval
        name: response_headers
        kval:
          - content-type
          - x-request-id
"""

    def _graphql_template(self, api: APIEndpoint, index: int) -> str:
        return f"""id: ios-graphql-introspect-{index:03d}

info:
  name: iOS GraphQL Introspection - {api.host}
  author: {self.author}
  severity: medium
  description: GraphQL introspection query exposed on iOS app backend.
  tags: ios,mobile,graphql,introspection

http:
  - method: POST
    path:
      - "{{{{BaseURL}}}}{api.path}"
    headers:
      Content-Type: application/json
      User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)
    body: |
      {{"query":"{{__schema{{types{{name fields{{name args{{name description type{{name}}}}}}}}}}}}"}}
    matchers-condition: and
    matchers:
      - type: status
        status:
          - 200
      - type: word
        part: body
        words:
          - '"__schema"'
          - '"types"'
        condition: and
      - type: dsl
        dsl:
          - "len(body) > 3000"
    extractors:
      - type: json
        name: schema_types
        json:
          - '.data.__schema.types[].name'
        part: body
      - type: regex
        name: sensitive_types
        part: body
        group: 1
        regex:
          - '"name"\\\\s*:\\\\s*"(User|Admin|Password|Token|Auth|Payment|Order|Customer)"'
"""

    def _admin_bypass_template(self, api: APIEndpoint, index: int) -> str:
        return f"""id: ios-admin-bypass-{index:03d}

info:
  name: iOS API Admin Endpoint Auth Bypass
  author: {self.author}
  severity: critical
  description: Admin endpoint detected without proper authorization.
  tags: ios,mobile,admin,auth-bypass

http:
  - method: {api.method}
    path:
      - "{{{{BaseURL}}}}{api.path}"
    headers:
      User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)
      Accept: application/json
    matchers-condition: and
    matchers:
      - type: status
        status:
          - 200
      - type: dsl
        dsl:
          - "status_code == 200"
          - '!contains(body, \\"Unauthorized\\")'
          - '!contains(body, \\"401\\")'
          - '!contains(body, \\"403\\")'
    extractors:
      - type: kval
        name: response_info
        kval:
          - content-type
          - server
      - type: regex
        name: api_version
        part: body
        group: 1
        regex:
          - '"version"\\\\s*:\\\\s*"([0-9.]+)"'
      - type: dsl
        name: response_size
        dsl:
          - "len(body)"
"""

    def _format_headers(self, headers: Dict[str, str]) -> str:
        skip = {'host', 'content-length', 'connection'}
        lines = []
        for k, v in headers.items():
            if k.lower() not in skip:
                lines.append(f"{k}: {v}")
        return "\n        ".join(lines) if lines else ""

    def _sanitize_filename(self, api: APIEndpoint) -> str:
        host = api.host.replace('.', '-')
        path = api.path.replace('/', '-').strip('-')
        path = re.sub(r'[^a-zA-Z0-9-]', '', path)[:40]
        return f"ios-{host}-{path}-{api.method.lower()}.yaml"
