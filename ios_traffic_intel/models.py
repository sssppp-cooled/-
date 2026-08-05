"""
数据模型层
与 go-ios / Rota / Nuclei 的数据结构对齐
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json


@dataclass
class APIEndpoint:
    """
    提取的 API 端点情报
    对应 Nuclei 的 target 格式: scheme://host/path
    """
    method: str
    host: str
    path: str
    scheme: str = "https"
    query_params: List[tuple] = field(default_factory=list)
    idor_params: List[tuple] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    request_body: Optional[str] = None
    response_status: int = 0
    response_size: int = 0
    timestamp: Optional[str] = None
    source_ip: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    @property
    def url(self) -> str:
        """Nuclei 可用的完整 URL"""
        return f"{self.scheme}://{self.host}{self.path}"

    @property
    def risk_score(self) -> int:
        """风险评分: IDOR 参数越多分越高"""
        score = len(self.idor_params) * 10
        if any(p[0] in ("user_id", "account_id") for p in self.idor_params):
            score += 20
        if "admin" in self.path.lower():
            score += 15
        return score

    @property
    def is_high_risk(self) -> bool:
        return self.risk_score >= 20

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "method": self.method,
            "host": self.host,
            "path": self.path,
            "query_params": self.query_params,
            "idor_params": self.idor_params,
            "risk_score": self.risk_score,
            "is_high_risk": self.is_high_risk,
            "timestamp": self.timestamp,
            "source_ip": self.source_ip,
            "tags": self.tags,
        }

    def to_nuclei_line(self) -> str:
        """导出为 Nuclei -list 文件的一行"""
        return self.url


@dataclass
class TrafficReport:
    """
    流量分析总报告
    可序列化为 JSON 供上游调度器消费
    """
    source_file: str
    total_entries: int = 0
    unique_apis: int = 0
    idor_targets: int = 0
    endpoints: List[APIEndpoint] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    goios_devices: List[str] = field(default_factory=list)

    def to_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "meta": {
                    "source": self.source_file,
                    "total_entries": self.total_entries,
                    "unique_apis": self.unique_apis,
                    "idor_targets": self.idor_targets,
                    "generated_at": self.generated_at,
                    "goios_devices": self.goios_devices,
                },
                "endpoints": [e.to_dict() for e in self.endpoints],
                "high_risk_urls": [e.url for e in self.endpoints if e.is_high_risk],
            }, f, indent=2, ensure_ascii=False)

    def summary(self) -> str:
        lines = [
            f"═══════════════════════════════════════",
            f"  Traffic Report: {self.source_file}",
            f"═══════════════════════════════════════",
            f"  总流量条目:     {self.total_entries}",
            f"  唯一 API 端点:  {self.unique_apis}",
            f"  IDOR 高危目标:  {self.idor_targets}",
            f"  关联设备:       {', '.join(self.goios_devices) or 'N/A'}",
            f"═══════════════════════════════════════",
        ]
        return "\n".join(lines)
