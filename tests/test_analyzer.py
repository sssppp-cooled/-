#!/usr/bin/env python3
"""
快速测试脚本 — 验证 ios-traffic-intel 安装
"""

from ios_traffic_intel import TrafficAnalyzer

test_har = {
    "log": {
        "entries": [
            {
                "startedDateTime": "2026-08-04T14:30:00Z",
                "request": {
                    "method": "GET",
                    "url": "https://api.target.com/v1/users/12345/profile?id=67890&token=abc",
                    "headers": [
                        {"name": "Authorization", "value": "Bearer eyJ..."},
                        {"name": "X-Forwarded-For", "value": "192.168.1.100"}
                    ]
                },
                "response": {"status": 200, "bodySize": 2048}
            },
            {
                "startedDateTime": "2026-08-04T14:30:01Z",
                "request": {
                    "method": "POST",
                    "url": "https://api.target.com/v1/orders/550e8400-e29b-41d4-a716-446655440000/pay",
                    "headers": [],
                    "postData": {"text": "{\"amount\": 99.99}"}
                },
                "response": {"status": 200, "bodySize": 512}
            },
            {
                "startedDateTime": "2026-08-04T14:30:02Z",
                "request": {
                    "method": "POST",
                    "url": "https://firebaseinstallations.googleapis.com/v1/projects/test/installations",
                    "headers": []
                },
                "response": {"status": 200, "bodySize": 256}
            },
            {
                "startedDateTime": "2026-08-04T14:30:03Z",
                "request": {
                    "method": "GET",
                    "url": "https://cdn.target.com/app.js",
                    "headers": []
                },
                "response": {"status": 200, "bodySize": 102400}
            }
        ]
    }
}

import json
import tempfile

with tempfile.NamedTemporaryFile(mode='w', suffix='.har', delete=False) as f:
    json.dump(test_har, f)
    har_path = f.name

analyzer = TrafficAnalyzer()
report = analyzer.parse_har(har_path, goios_udids=["00008101-0000000000000000"])

assert report.total_entries == 4, "总条目数不对"
assert report.unique_apis == 2, "应该过滤掉 2 个噪声"
assert report.idor_targets == 2, "应该有 2 个 IDOR 目标"
assert report.endpoints[0].is_high_risk, "第一个应该是高危"

print("\n✅ 所有测试通过！")
