#!/usr/bin/env python3
"""
iOS Traffic Intel CLI
═══════════════════════════════════════════════════════════════
用法:
    ios-traffic parse har_file.har --output-dir ./out
    ios-traffic generate report.json --output-dir ./nuclei-templates
    ios-traffic parse har_file.har --auto-generate --output-dir ./out
═══════════════════════════════════════════════════════════════
"""

import argparse
import sys
from pathlib import Path

from .analyzer import TrafficAnalyzer
from .template_generator import TemplateGenerator


def main():
    parser = argparse.ArgumentParser(
        prog="ios-traffic",
        description="iOS app traffic analyzer for bug bounty & security testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
集成链:
  go-ios (Go) → 管理 iOS 设备、启动 WDA、安装应用
      ↓
  mitmproxy / Burp → 捕获 HTTPS 流量 → .har
      ↓
  ios-traffic parse → 解析 HAR、提取 API、检测 IDOR
      ↓
  ios-traffic generate → 自动生成 Nuclei YAML 模板
      ↓
  Nuclei (Go) → 扫描后端 API 漏洞
      ↓
  Rota (Go) → 代理池出口（可选，用于绕过 WAF）
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    parse_cmd = subparsers.add_parser("parse", help="解析 HAR 流量文件")
    parse_cmd.add_argument("har_file", help="HAR 文件路径")
    parse_cmd.add_argument("-o", "--output-dir", default="./out",
                           help="输出目录 (默认: ./out)")
    parse_cmd.add_argument("--goios-udid", default="",
                           help="关联的 go-ios 设备 UDID，逗号分隔")
    parse_cmd.add_argument("--filter", choices=["all", "idor", "high-risk"],
                           default="all", help="过滤目标类型")
    parse_cmd.add_argument("--export-json", action="store_true",
                           help="导出完整 JSON 报告")
    parse_cmd.add_argument("--auto-generate", action="store_true",
                           help="自动生成 Nuclei 模板")

    gen_cmd = subparsers.add_parser("generate", help="从 JSON 报告生成 Nuclei 模板")
    gen_cmd.add_argument("report_json", help="traffic_report.json 路径")
    gen_cmd.add_argument("-o", "--output-dir", default="./nuclei-templates",
                         help="模板输出目录")

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    args = parser.parse_args()

    if args.command == "parse":
        _cmd_parse(args)
    elif args.command == "generate":
        _cmd_generate(args)
    else:
        parser.print_help()
        sys.exit(1)


def _cmd_parse(args):
    har_path = Path(args.har_file)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    udid_list = [u.strip() for u in args.goios_udid.split(",") if u.strip()]

    analyzer = TrafficAnalyzer()
    report = analyzer.parse_har(str(har_path), goios_udids=udid_list)

    target_file = out_dir / "nuclei_targets.txt"
    if args.filter == "idor":
        analyzer.export_idor_targets(report, str(target_file))
    elif args.filter == "high-risk":
        analyzer.export_nuclei_targets(
            [e for e in report.endpoints if e.is_high_risk],
            str(target_file)
        )
    else:
        analyzer.export_nuclei_targets(report.endpoints, str(target_file))

    if any(e.idor_params for e in report.endpoints):
        idor_file = out_dir / "nuclei_idor_targets.txt"
        analyzer.export_idor_targets(report, str(idor_file))

    ip_file = out_dir / "rota_source_ips.txt"
    analyzer.export_rota_source_ips(report, str(ip_file))

    json_file = out_dir / "traffic_report.json"
    report.to_json(str(json_file))

    if args.auto_generate:
        template_dir = out_dir / "nuclei-templates"
        gen = TemplateGenerator()
        gen.from_endpoints(report.endpoints, str(template_dir))

    print(f"\n[*] 全部输出在: {out_dir.resolve()}")


def _cmd_generate(args):
    import json
    report_path = Path(args.report_json)
    if not report_path.exists():
        print(f"[!] 报告文件不存在: {args.report_json}")
        sys.exit(1)

    with open(report_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    endpoints = []
    for e in data.get("endpoints", []):
        endpoints.append(APIEndpoint(**{
            k: v for k, v in e.items()
            if k in ["method", "host", "path", "scheme", "query_params",
                     "idor_params", "headers", "request_body", "response_status",
                     "response_size", "timestamp", "source_ip", "tags"]
        }))

    gen = TemplateGenerator()
    gen.from_endpoints(endpoints, args.output_dir)


if __name__ == "__main__":
    main()
