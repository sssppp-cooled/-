
base_dir = "/mnt/agents/output/ios-traffic-intel"

# ===== scripts/verify_rota_pool.py =====
verify_script = r'''#!/usr/bin/env python3
"""
verify_rota_pool.py — Rota 代理池地理验证脚本
═══════════════════════════════════════════════════════════════
用法:
    python scripts/verify_rota_pool.py --pool-id 1 --rota-url http://rota:80 --token $TOKEN
    python scripts/verify_rota_pool.py --pool-id 1 --rota-url http://rota:80 --token $TOKEN --write-tags
    python scripts/verify_rota_pool.py --pool-id 1 --rota-url http://rota:80 --token $TOKEN --filter-v4 --min-confidence 80

写回 Rota 标签格式:
    us_residential=true/false
    confidence=85.5
    ipv6=false
    checked_at=1722825600

过滤用法:
    --filter-v4          只保留 IPv4 代理
    --filter-v6          只保留 IPv6 代理
    --min-confidence 80  只保留 confidence >= 80 的代理
═══════════════════════════════════════════════════════════════
"""

import argparse
import json
import sys
import time
from pathlib import Path

# 将项目根目录加入路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ios_traffic_intel.geo_validator import GeoValidator, RotaPoolVerifier


def main():
    parser = argparse.ArgumentParser(
        prog="verify_rota_pool",
        description="Verify Rota proxy pool geo-location and write back tags",
    )
    parser.add_argument("--pool-id", type=int, required=True, help="Rota pool ID")
    parser.add_argument("--rota-url", default="http://localhost", help="Rota API URL")
    parser.add_argument("--token", required=True, help="Rota JWT token")
    parser.add_argument("--write-tags", action="store_true", help="Write verification results back to Rota as proxy tags")
    parser.add_argument("--filter-v4", action="store_true", help="Only keep IPv4 proxies")
    parser.add_argument("--filter-v6", action="store_true", help="Only keep IPv6 proxies")
    parser.add_argument("--min-confidence", type=float, default=0, help="Minimum confidence score (0-100)")
    parser.add_argument("--output", "-o", default="./out/rota_verification.json", help="Output report path")
    parser.add_argument("--ipinfo-token", default=None, help="IPinfo API token")
    parser.add_argument("--ipqs-key", default=None, help="IPQualityScore API key")
    parser.add_argument("--ripe-key", default=None, help="RIPE Atlas API key")

    args = parser.parse_args()

    # 初始化验证器
    geo = GeoValidator(
        ipinfo_token=args.ipinfo_token,
        ipqs_key=args.ipqs_key,
        ripe_atlas_key=args.ripe_key,
    )
    verifier = RotaPoolVerifier(
        rota_api_url=args.rota_url,
        rota_token=args.token,
        geo_validator=geo,
    )

    # 执行验证
    print(f"[*] 开始验证 Rota Pool #{args.pool_id}...")
    report = verifier.verify_pool(args.pool_id)

    # 过滤结果
    filtered = report["details"]
    if args.filter_v4:
        filtered = [d for d in filtered if not d["ipv6"]]
        print(f"[*] IPv4 过滤后: {len(filtered)} 个")
    if args.filter_v6:
        filtered = [d for d in filtered if d["ipv6"]]
        print(f"[*] IPv6 过滤后: {len(filtered)} 个")
    if args.min_confidence > 0:
        filtered = [d for d in filtered if d["confidence"] >= args.min_confidence]
        print(f"[*] Confidence >= {args.min_confidence} 过滤后: {len(filtered)} 个")

    report["filtered_details"] = filtered
    report["filter_applied"] = {
        "v4_only": args.filter_v4,
        "v6_only": args.filter_v6,
        "min_confidence": args.min_confidence,
    }

    # 写回标签
    if args.write_tags:
        from ios_traffic_intel.geo_validator import GeoVerificationResult
        results = [GeoVerificationResult(**{
            "ip": d["ip"],
            "is_valid_us_residential": d["is_valid_us_residential"],
            "confidence": d["confidence"],
            "ipv6": d["ipv6"],
            "checks": d["checks"],
            "warnings": d["warnings"],
            "checked_at": d["checked_at"],
        }) for d in filtered]
        verifier.write_back_tags(args.pool_id, results)

    # 输出报告
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"[+] 报告已保存: {out_path}")
    print(f"\n{'='*50}")
    print(f"Pool #{args.pool_id} 验证摘要")
    print(f"{'='*50}")
    print(f"  总代理数:     {report['total_proxies']}")
    print(f"  有效住宅IP:   {report['valid_us_residential']}")
    print(f"  无效代理:     {report['invalid']}")
    print(f"  有效率:       {report['validity_rate']*100:.1f}%")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
'''

with open(f"{base_dir}/scripts/verify_rota_pool.py", "w", encoding="utf-8") as f:
    f.write(verify_script)

# 给脚本加执行权限
import stat
os.chmod(f"{base_dir}/scripts/verify_rota_pool.py", 
         os.stat(f"{base_dir}/scripts/verify_rota_pool.py").st_mode | stat.S_IEXEC)

print("scripts/verify_rota_pool.py 创建完成")
