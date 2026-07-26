#!/usr/bin/env python3
"""Validate data/ip_ranges.json against schemas/egress_ips.schema.json using jsonschema.

Usage: python scripts/validate_schema.py
"""
import json
from pathlib import Path
import sys

try:
    import jsonschema
except ImportError:
    print("jsonschema not installed. Please pip install jsonschema", file=sys.stderr)
    raise


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ip_ranges.json"
SCHEMA = ROOT / "schemas" / "egress_ips.schema.json"


def main():
    with open(SCHEMA, "r", encoding="utf-8") as f:
        schema = json.load(f)
    with open(DATA, "r", encoding="utf-8") as f:
        data = json.load(f)

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if not errors:
        print("OK: data/ip_ranges.json validates against schema.")
        return 0

    print("Validation errors:")
    for e in errors:
        print(f"- {'/'.join(map(str, e.path))}: {e.message}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
