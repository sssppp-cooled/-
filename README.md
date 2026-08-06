<p align="center">
  <img src="./banner.png" alt="Project Banner" width="100%">
</p>

<h1 align="center">iOS Traffic Intel</h1>
<p align="center">三源交叉验证（GeoIP 35% + ASN 40% + IPQS 25%）· 美国住宅 IP 置信度评分系统</p>

## 🎯 主角工具：verify_rota_pool.py

> [!IMPORTANT]
> **出身**：本脚本是 [go-ios](https://github.com/danielpaulus/go-ios) 所带来灵感的延伸。正如 go-ios 让 iOS 设备控制变得开放、可脚本化，`verify_rota_pool.py` 把“美国住宅 IP 地理验证”变成了自动化闭环。
> **闭环**：从您自建的代理池调度中心拉取代理列表 ➡️ 送入三源交叉验证模型 ➡️ 写回标签（US_Residential / Datacenter / 置信度分数）。

> [!NOTE]
> **三源交叉验证模型（权重与检查项）**
> - **① 多源 GeoIP 比对（35%）**：IPinfo + IP-API + MaxMind ➡️ 国家是否一致 = US？一致性 ≥ 67%？
> - **② ASN + BGP 分析（40%）**：Team Cymru whois ➡️ ASN 是否美国注册？前缀粒度 /24+？已知住宅 ISP？
> - **③ 外部实证（25%）**：IPQualityScore ➡️ fraud_score ≤ 50？residential = True？

> [!WARNING]
> **IPv6 降级策略**：IPv6 地理精度仅 40–80% ➡️ 置信度整体 ×0.7 惩罚，阈值收紧为 confidence ≥ 70、checks_passed ≥ 3。

## 🏗️ 架构与分工

| 组件 | 语言 | 职责 | 不做什么 |
|---|---|---|---|
| `ios_traffic_intel` | Python | HAR 解析、API 提取、IDOR 代理池管理 | 流量内容分析 |
| `GeoValidator` | Python | 多源 GeoIP + ASN 验证、置信度打分 | 设备控制 |
| `自建代理池调度中心` | Go/Python | 代理池调度、健康检查、IP 轮换、API 提供 | 流量内容分析 |
| `go-ios` | Go | iOS 设备管理、WDA 部署 | 代理池、漏洞扫描 |

<details>
<summary>📂 点击展开：项目目录结构</summary>

```text
.
├── ios_traffic_intel/      # 核心库：流量解析、API 提取、漏洞检测逻辑
│   ├── parsers/            # HAR / pcap 解析器
│   ├── analyzers/          # IDOR / BOLA 模式检测
│   └── validators/         # GeoIP / ASN 验证引擎
├── scripts/                # 命令行工具与自动化脚本
│   └── verify_rota_pool.py # 主角：代理池验证闭环脚本
├── tests/                  # 单元测试
└── docs/                   # 文档与参考资料
