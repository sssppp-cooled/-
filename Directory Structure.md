api-bounty-intel/
│
├── main.py                          # CLI 入口 (Typer)
├── config.py                        # 全局配置加载 (Pydantic)
│
│── ── 核心业务层 (Core) ────────────────────────────────────────
├── core/
│   ├── target_scheduler.py          # IoT 目标调度与 Token 负载均衡
│   ├── bounty_matcher.py            # H1/BC Scope 匹配引擎
│   └── anomaly_detector.py          # 流量/UI 异常检测 (基于基线)
│
│── ── 设备农场控制面 (Device Farm Control) ─────────────────────
├── device_farm/
│   ├── go_ios_client.py             # ★ go-ios REST-API 客户端 (核心)
│   ├── node_manager.py              # 节点生命周期 (发现/配对/重启)
│   └── signing_service.py           # Apple 自动签名与描述文件管理
│
│── ── UI 自动化层 (Automation) ─────────────────────────────────
├── automation/
│   ├── lightweight_driver.py        # ★ 直连 DeviceKit/WDA 的轻量驱动
│   ├── ui_tree_parser.py            # UI 树解析 (XPath/CSS 选择器)
│   └── action_executor.py           # 动作执行器 (结合 UI 树和坐标)
│
│── ── 情报收集数据面 (Intelligence Data) ───────────────────────
├── intelligence/
│   ├── pcap_listener.py             # ★ pymobiledevice3 pcapd 实时抓包
│   ├── syslog_listener.py           # 系统日志捕获 (寻找泄露的 Token)
│   └── sandbox_reader.py            # App 沙盒文件读取 (硬编码配置)
│
│── ── 网络与代理池 (Network & Proxy) ───────────────────────────
├── network/
│   ├── proxyhat_pool.py             # ProxyHat 住宅代理池 (Sticky/Rotate)
│   └── proxy_injector.py            # 调用 go-ios 将代理注入设备全局网络
│
│── ── 监控与告警 (Monitoring) ──────────────────────────────────
├── monitoring/
│   ├── metrics_collector.py         # 收集设备/代理/Token 指标 (Prometheus)
│   └── alerter.py                   # 异常告警 (Telegram/Slack)
│
│── ── 部署与配置 (Setup) ───────────────────────────────────────
├── setup/
│   ├── install_go_ios.sh            # 下载 go-ios 二进制并启动 REST-API
│   ├── setup_linux_usb.sh           # 配置 Linux udev USB 权限
│   └── device_config.json           # 物理设备清单 (UDID, 角色)
│
├── tests/                           # Pytest 单元/集成测试
├── docs/                            # MkDocs 文档
├── docker-compose.yml               # 一键拉起 go-ios REST-API + Redis + Prometheus
├── requirements.txt                 # Python 依赖
├── .env.example                     # 环境变量模板
└── .gitignore
