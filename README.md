# 5. README.rst（替换 README.md）
readme_rst = '''iOS Traffic Intel
===============

iOS 应用流量情报分析器。从 HAR/mitmproxy 流量中提取 API 端点、检测 IDOR/BOLA 模式，
输出给 **Nuclei** 扫描器和 **Rota** 代理池。

架构定位
--------

::

    iOS Device (go-ios 管理, Go)
           | USB / Userspace Tunnel
           v
    Traffic Capture (mitmproxy / Burp / pcapd)
           | .har / .mitm / .pcap
           v
    TrafficAnalyzer (本模块) --> Nuclei targets
           |
           v
    TemplateGenerator ---------> 自动生成 Nuclei YAML
           |
           v
    GeoValidator ----------------> 多源 GeoIP + ASN + RIPE Atlas 验证
           |
           v
    Rota Proxy Pool (Go) ------> 后端 API 扫描

**明确分工：**

=================== ====== =========================== ===================
组件                 语言   职责                        不做什么
=================== ====== =========================== ===================
ios_traffic_intel    Python HAR 解析、API 提取、IDOR   代理池管理、设备控制
Rota                 Go     代理池、健康检查、IP 轮换    流量内容分析
go-ios               Go     iOS 设备管理、WDA 部署       代理池、漏洞扫描
Nuclei               Go     漏洞扫描、API 安全测试       设备管理、代理池
=================== ====== =========================== ===================

安装
----

.. code-block:: bash

    git clone https://github.com/sssppp-cooled/-/git
    cd ios-traffic-intel
    git submodule update --init --recursive
    pip install -e .

用法
----

解析 HAR
~~~~~~~~

.. code-block:: bash

    ios-traffic parse traffic.har --filter idor --export-json --output-dir ./out

输出：

- ``./out/nuclei_targets.txt`` — Nuclei 扫描目标
- ``./out/nuclei_idor_targets.txt`` — 仅 IDOR 高危
- ``./out/rota_source_ips.txt`` — 源 IP 情报
- ``./out/traffic_report.json`` — 完整 JSON 报告

验证 Rota 代理池
~~~~~~~~~~~~~~~~

.. code-block:: bash

    python scripts/verify_rota_pool.py \\
        --pool-id 1 \\
        --rota-url http://rota-server:80 \\
        --token $ROTA_JWT \\
        --filter-v4 \\
        --min-confidence 80 \\
        --write-tags

写回 Rota 的标签：

- ``us_residential=true/false``
- ``confidence=85.5``
- ``ipv6=false``
- ``checked_at=1722825600``

目录结构
--------

见 ``docs/structure.md``

License
-------

MIT
