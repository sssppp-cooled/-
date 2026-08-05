# 同时创建 docs/index.md（MkDocs 首页，对应 nav 里的 Home）
index_md = '''# iOS Traffic Intel

iOS application traffic intelligence analyzer.

Extract API endpoints from HAR/mitmproxy captures, detect IDOR/BOLA patterns,
and output targets for **Nuclei** scanner and **Rota** proxy pool.

## Quick Start

```bash
pip install -e .
ios-traffic parse traffic.har --filter idor --output-dir ./out
```

## Architecture

```
iOS Device (go-ios managed)
       |
Traffic Capture (mitmproxy / Burp)
       |
TrafficAnalyzer (this module)
       |
   +---> Nuclei targets
   +---> Auto-generated YAML templates
   +---> GeoValidator (US residential proxy verification)
```

## Modules

| Module | Class | Purpose |
|--------|-------|---------|
| `analyzer.py` | `TrafficAnalyzer` | HAR parsing, IDOR/BOLA detection |
| `template_generator.py` | `TemplateGenerator` | Auto-generate Nuclei YAML from endpoints |
| `geo_validator.py` | `GeoValidator` | Multi-source GeoIP + ASN + RIPE Atlas verification |
| `cli.py` | — | Command-line entry: `ios-traffic parse / generate` |

## Naming Constitution v1

- Package: `ios_traffic_intel` (underscores only)
- Modules: `analyzer.py`, `template_generator.py`, `geo_validator.py`, `cli.py`, `models.py`
- Classes: `TrafficAnalyzer`, `TemplateGenerator`, `GeoValidator`
- Scripts: `scripts/verify_rota_pool.py`
'''

with open(f"{base_dir}/docs/index.md", "w", encoding="utf-8") as f:
    f.write(index_md)
