ssspppp-cooled/-
├── .github/
│   └── workflows/
│       └── docs.yml              # GitHub Actions CI（lint + test）
│
├── ios_traffic_intel/            # Python 包（命名宪法：仅下划线）
│   ├── init.py               # 包入口，导出核心类
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
│   ├── index.md                  # MkDocs 首页
│   └── structure.md              # 本文件：目录结构说明
│
├── mkdocs.yml                    # MkDocs 站点配置
├── README.rst                    # 项目主页（reStructuredText）
├── .gitmodules                   # Git Submodule 声明
├── .gitignore
├── pyproject.toml                # 现代 Python 项目配置
└── setup.py                      # pip 安装入口
