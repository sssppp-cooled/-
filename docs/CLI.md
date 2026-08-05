api-bounty-intel/
│
├── main.py                        # CLI 入口（含可选 adb 命令组）
├── config.py                      # 配置（★ ENABLE_ADB 开关）
│
│── ── 负载均衡层 ─────────────────────────────────────
├── unified_pool.py                # 统一调度 + 故障转移 + 健康检查
├── monitor.py                     # ★ 监控指标 + 告警
│
│── ── 代理源层（可插拔）─────────────────────────────
├── ios_proxy_pool.py              # 源1: iPhone 热点（默认启用）
├── adb_proxy_pool.py              # 源2: ADB 真机（ENABLE_ADB=true 时启用）
├── proxy_pool.py                  # 源3: 静宅住宅（兜底）
│
│── ── 业务逻辑层 ─────────────────────────────────────
├── h1_client.py                   # H1: 4 个 IoT 目标，美国走美卡
├── bc_client.py                   # BC: IoT 优先
├── traffic_listener.py            # Burp XML / HAR 解析
│
│── ── 部署脚本 ───────────────────────────────────────
├── setup/
│   ├── ios_setup.sh / .bat        # iPhone 环境（必装）
│   ├── adb_setup.sh / .bat        # ADB 环境（可选）
│   ├── gnirehtet_setup.sh         # gnirehtet（可选）
│   ├── device_config.json         # 橙卡/白卡 + Android 清单
│   └── number_lookup.py           # 号码段归属解析
│
│── ── 文档 ───────────────────────────────────────────
├── docs/
│   ├── index.md
│   ├── quick-start.md
│   ├── ios-deploy-guide.md        # iPhone 部署
│   ├── adb-deploy-guide.md        # ADB 部署（可选章节）
│   ├── proxy-architecture.md      # 本文架构图
│   ├── cli-reference.md
│   ├── changelog.md
│   ├── requirements.txt
│   └── api/
│       ├── proxy_pool.md
│       ├── ios_proxy_pool.md
│       ├── adb_proxy_pool.md
│       ├── unified_pool.md
│       ├── monitor.md
│       ├── h1_client.md
│       └── traffic_listener.md
│
├── scripts/generate_cli_docs.py
│
│── ── CI/CD ──────────────────────────────────────────
├── .github/workflows/ci.yml
├── .github/workflows/docs.yml
├── mkdocs.yml
├── .readthedocs.yaml
├── cliff.toml
│
├── requirements.txt
├── .env.example                   # ★ 含 ENABLE_ADB=false
├── .gitignore                     # 含 device_config.json
└── LICENSE
