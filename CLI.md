main.py
 ├── unified_pool.py ──────────────┐
 │    ├── ios_proxy_pool.py        │──▶ Redis
 │    ├── adb_proxy_pool.py  [if ENABLE_ADB]
 │    ├── proxy_pool.py ───────────│──▶ Redis + 静宅API
 │    └── monitor.py ──────────────│──▶ Redis metrics
 ├── h1_client.py ──▶ unified_pool
 ├── bc_client.py ──▶ unified_pool
 └── traffic_listener.py ──▶ proxy_pool
