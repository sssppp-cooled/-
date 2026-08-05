api-bounty-intel/
├── main.py                    # CLI（ios setup / ios run 替换热点命令）
├── config.py
├── proxy_pool.py              # ★ 唯一 IP 源（静宅）
├── ios_node.py                # ★ 新增：无卡 iPhone 节点（Appium+WDA）
├── h1_client.py               # 走 proxy_pool
├── bc_client.py
├── traffic_listener.py        # 可选: pcapd 真机抓包
├── setup/
│   ├── ios_setup.sh           # 装 pymobiledevice3 + appium
│   ├── device_config.json     # udid + 型号（无 SIM 字段）
│   └── number_lookup.py       # 可删（无卡用不上）
├── docs/ ...
└── ...
