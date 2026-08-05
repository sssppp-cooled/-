# 3. docs/structure.md（目录结构说明）
structure_md = '''# 目录结构

```
ssspppp-cooled/-
├── .github/
│   └── workflows/
│       └── docs.yml              # GitHub Actions CI（lint + test）
│
├── ios_traffic_intel/            # Python 包（命名宪法：仅下划线）
│   ├── __init__.py               # 包入口，导出核心类
│   ├── analyzer.py               # TrafficAnalyzer — HAR 解析 + IDOR 检测
│   ├── template_generator.py     # TemplateGenerator — 自动生成 Nuclei YAML
│   ├── geo_validator.py          # GeoValidator — 多源 GeoIP + ASN + RIPE Atlas
│   ├── cli.py                    # 命令行入口：ios-traffic parse / generate
│   └── models.py                 # 数据模型：APIEndpoint, TrafficReport
│
├── third_party/                  # Git Submodule（第三方库，不阉割）
│   ├── geoip-all-in-one/         # daijro — 多源 GeoIP 合并 MMDB
│   ├── asn/                      # nitefood — ASN + BGP + RPKI + 路由追踪
│   └── ripe-atlas-cousteau/      # RIPE NCC — RIPE Atlas 主动测量 API
│
├── scripts/                      # 独立脚本
│   └── verify_rota_pool.py       # Rota 代理池地理验证 + 标签回写
│
├── docs/                         # 文档
│   ├── CLI.md                    # 命令行参考
│   └── structure.md              # 本文件：目录结构说明
│
├── mkdocs.yml                    # MkDocs 站点配置
├── README.rst                    # 项目主页（reStructuredText）
├── .gitmodules                   # Git Submodule 声明
├── .gitignore
├── pyproject.toml                # 现代 Python 项目配置
└── setup.py                      # pip 安装入口
```

## 命名宪法 v1

| 层级 | 规则 |
|------|------|
| 包目录 | `ios_traffic_intel` — 仅下划线，禁用连字符 |
| 模块 | `analyzer.py`, `template_generator.py`, `geo_validator.py`, `cli.py`, `models.py` |
| 类 | `TrafficAnalyzer`, `TemplateGenerator`, `GeoValidator` |
| 脚本 | `scripts/verify_rota_pool.py` |
| 禁用名 | `ios-traffic-intel`, `intel_toolkit`, `api-bounty-intel`, `main.py`, `pattern_extractor.py`, `report_generator.py` |

## 职责边界

| 组件 | 语言 | 职责 | 不做什么 |
|------|------|------|---------|
| **ios_traffic_intel** | Python | HAR 解析、API 提取、IDOR 检测、模板生成、Geo 验证 | 代理池管理、设备控制 |
| **Rota** | Go | 代理池、健康检查、IP 轮换、GeoIP、Webhook 告警 | 流量内容分析 |
| **go-ios** | Go | iOS 设备管理、WDA 部署、USB 隧道 | 代理池、漏洞扫描 |
| **Nuclei** | Go | 漏洞扫描、API 安全测试 | 设备管理、代理池 |
'''

with open(f"{base_dir}/docs/structure.md", "w", encoding="utf-8") as f:
    f.write(structure_md)
