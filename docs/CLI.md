base_dir = "/mnt/agents/output/ios-traffic-intel"

# 1. 创建 docs 目录
os.makedirs(f"{base_dir}/docs", exist_ok=True)

# 2. docs/CLI.md
cli_md = '''# CLI 参考

## `ios-traffic parse`

解析 HAR 流量文件，提取 API 端点、检测 IDOR/BOLA。

```bash
ios-traffic parse <har_file> [选项]
```

| 选项 | 说明 |
|------|------|
| `-o, --output-dir` | 输出目录（默认 `./out`） |
| `--goios-udid` | 关联的 go-ios 设备 UDID，逗号分隔 |
| `--filter` | `all` / `idor` / `high-risk` |
| `--export-json` | 导出完整 JSON 报告 |
| `--auto-generate` | 自动生成 Nuclei 模板 |

### 示例

```bash
# 基础解析
ios-traffic parse traffic.har

# 仅导出 IDOR 目标
ios-traffic parse traffic.har --filter idor

# 关联 go-ios 设备并自动生成模板
ios-traffic parse traffic.har \
    --goios-udid "00008101-0000000000000000" \
    --auto-generate \
    --output-dir ./out
```

## `ios-traffic generate`

从 JSON 报告生成 Nuclei 模板。

```bash
ios-traffic generate <report_json> [选项]
```

| 选项 | 说明 |
|------|------|
| `-o, --output-dir` | 模板输出目录（默认 `./nuclei-templates`） |

### 示例

```bash
ios-traffic generate ./out/traffic_report.json --output-dir ./templates
```

## `scripts/verify_rota_pool.py`

验证 Rota 代理池地理归属。

```bash
python scripts/verify_rota_pool.py [选项]
```

| 选项 | 说明 |
|------|------|
| `--pool-id` | Rota 池 ID（必填） |
| `--rota-url` | Rota API 地址（默认 `http://localhost`） |
| `--token` | Rota JWT Token（必填） |
| `--write-tags` | 将结果写回 Rota 代理标签 |
| `--filter-v4` | 仅保留 IPv4 代理 |
| `--filter-v6` | 仅保留 IPv6 代理 |
| `--min-confidence` | 最小置信度（0-100） |
| `--ipinfo-token` | IPinfo API Token |
| `--ipqs-key` | IPQualityScore API Key |
| `--ripe-key` | RIPE Atlas API Key |

### 示例

```bash
# 基础验证
python scripts/verify_rota_pool.py \
    --pool-id 1 \
    --rota-url http://rota-server:80 \
    --token $ROTA_JWT

# 只保留 IPv4 且 confidence >= 80 的代理，并写回标签
python scripts/verify_rota_pool.py \
    --pool-id 1 \
    --rota-url http://rota-server:80 \
    --token $ROTA_JWT \
    --filter-v4 \
    --min-confidence 80 \
    --write-tags
```
'''

with open(f"{base_dir}/docs/CLI.md", "w", encoding="utf-8") as f:
    f.write(cli_md)
