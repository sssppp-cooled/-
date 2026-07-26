#!/usr/bin/env python3
"""Retrieve IP ranges by service and/or direction from data/ip_ranges.json.

Usage examples:
  python scripts/get_ip_ranges.py --service API
  python scripts/get_ip_ranges.py --direction EGRESS
  python scripts/get_ip_ranges.py --service EMAIL --direction EGRESS
"""
import argparse
import json
from pathlib import Path


def load_data():
    p = Path(__file__).resolve().parents[1] / "data" / "ip_ranges.json"
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
    p = argparse.ArgumentParser()
    p.add_argument("--service", help="Service name to filter (e.g. API, EMAIL, DNS, WEB_SCRAPING)")
    p.add_argument("--direction", help="Direction to filter (EGRESS or INGRESS)")
    p.add_argument("--file", help="Path to JSON file (overrides bundled data)")
    args = p.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = load_data()

    out = filter_data(data, service=args.service, direction=args.direction)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
