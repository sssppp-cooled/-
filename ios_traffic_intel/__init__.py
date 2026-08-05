"""
iOS Traffic Intelligence
═══════════════════════════════════════════════════════════════
从 iOS 应用流量中提取 API 端点情报，检测 IDOR/BOLA 模式。
与 go-ios (Go) + Rota (Go) + Nuclei (Go) 组成完整安全测试链。

架构:
    iOS Device (go-ios 管理)
           │ USB / Userspace Tunnel
           ▼
    Traffic Capture (mitmproxy / Burp / pcapd)
           │ .har / .mitm / .pcap
           ▼
    TrafficAnalyzer (本模块) ──▶ Nuclei targets
           │
           ▼
    TemplateGenerator ─────────▶ 自动生成 Nuclei YAML
           │
           ▼
    Rota Proxy Pool (Go) ──────▶ 后端 API 扫描
═══════════════════════════════════════════════════════════════
"""

__version__ = "0.1.0"
__author__ = "sssppp-cooled"

from .analyzer import TrafficAnalyzer
from .models import APIEndpoint, TrafficReport
from .template_generator import TemplateGenerator
from .geo_validator import GeoValidator

__all__ = ["TrafficAnalyzer", "APIEndpoint", "TrafficReport", "TemplateGenerator", "GeoValidator"]
