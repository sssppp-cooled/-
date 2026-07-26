#!/usr/bin/env python3
"""啊昊：按服务(service)和方向(direction)检索出口 IP 范围的爬虫脚本。"""
import argparse
import json
from pathlib import Path


def load_data():
    p = Path(__file__).resolve().parent / "data" / "ip_ranges.json"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_data(data, service=None, direction=None):
    results = data.get("results", [])
    def match(item):
        if service and item.get("service") != service:
            return False
        if direction and item.get("direction") != direction:
            return False
        return True
    return {"results": [i for i in results if match(i)]}


def main():
    parser = argparse.ArgumentParser(description="啊昊：检索出口 IP 范围")
    parser.add_argument("--service", help="服务名称，例如 API、EMAIL、DNS、WEB_SCRAPING")
    parser.add_argument("--direction", help="方向，例如 EGRESS 或 INGRESS")
    parser.add_argument("--file", help="JSON 文件，若指定则覆盖内置数据")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = load_data()

    out = filter_data(data, service=args.service, direction=args.direction)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
