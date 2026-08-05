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
ios-traffic parse traffic.har \\
    --goios-udid "00008101-0000000000000000" \\
    --auto-generate \\
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
