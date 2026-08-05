# go-ios 集成指南

&gt; go-ios 是 iOS 设备管理的核心（Go 语言），本模块（Python）只消费它产生的流量文件。

## 架构关系
┌─────────────────────────────────────────────────────────────┐
│  go-ios (Go) — 设备控制层                                    │
│  ├─ ios list                    列出设备                     │
│  ├─ ios runwda --udid=xxx       启动 WebDriverAgent          │
│  ├─ ios install --path=app.ipa  安装应用                     │
│  ├─ ios launch com.bundle.id    启动应用                     │
│  ├─ ios api                     启动 REST API 服务          │
│  └─ ios syslog --udid=xxx       获取系统日志                 │
│                                                             │
│  输出: USB 隧道 / REST API / 日志文件                         │
└──────────────────────────────┬──────────────────────────────┘
│
┌──────────────────────────────▼──────────────────────────────┐
│  Traffic Capture — 流量捕获层                                │
│  ├─ mitmproxy -p 8080 --mode regular                        │
│  ├─ Burp Suite (导出 HAR)                                   │
│  └─ go-ios pcapd (直接抓包)                                 │
│                                                             │
│  输出: .har / .mitm / .pcap                                 │
└──────────────────────────────┬──────────────────────────────┘
│
┌──────────────────────────────▼──────────────────────────────┐
│  ios-traffic-intel (Python) — 情报分析层                     │
│  ├─ parse_har()                 解析流量                     │
│  ├─ detect_idor()               IDOR/BOLA 检测               │
│  └─ export_nuclei_targets()     导出扫描目标                 │
│                                                             │
│  输出: nuclei_targets.txt / traffic_report.json               │
└──────────────────────────────┬──────────────────────────────┘
│
┌──────────────────────────────▼──────────────────────────────┐
│  Nuclei (Go) — 漏洞扫描层                                   │
│  └─ nuclei -list targets.txt -t templates/                  │
│                                                             │
│  可选: 通过 Rota (Go) 代理池出口                            │
│  export HTTP_PROXY=http://user:pass@rota:8000               │
└─────────────────────────────────────────────────────────────┘

## 为什么 go-ios 用 Go，本模块用 Python？

| 考量 | go-ios (Go) | 本模块 (Python) |
|------|-------------|-----------------|
| 性能 | USB 通信需要零拷贝、低延迟 | 流量解析是 IO 密集型，Python 足够 |
| 生态 | iOS 底层协议（lockdownd、usbmuxd）已有 Go 实现 | HAR 解析、正则、数据处理 Python 更顺手 |
| 部署 | 单二进制，跨平台 | pip 安装，脚本化 |
| 维护 | 社区活跃，danielpaulus 维护 | 你自定义的业务逻辑 |

**不要试图用 Python 重写 go-ios 的设备管理功能。** 通过它的 REST API 或命令行调用即可。

## 完整工作流脚本

```bash
#!/bin/bash
# run_ios_bounty.sh — 完整的 iOS 漏洞赏金扫描流水线

UDID="${1:-00008101-0000000000000000}"
APP_BUNDLE="${2:-com.target.app}"
OUTPUT_DIR="./out/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "═══════════════════════════════════════════"
echo "  iOS Bug Bounty Scan Pipeline"
echo "  Device: $UDID"
echo "  Target: $APP_BUNDLE"
echo "═══════════════════════════════════════════"

# 1. go-ios: 确保设备连接
echo "[*] 检查设备..."
ios list | grep "$UDID" || { echo "[!] 设备未连接"; exit 1; }

# 2. go-ios: 安装应用（如需要）
# ios install --path=target.ipa --udid=$UDID

# 3. go-ios: 启动 WDA
echo "[*] 启动 WebDriverAgent..."
ios runwda --udid=$UDID &
WDA_PID=$!
sleep 3

# 4. go-ios: 启动应用
echo "[*] 启动目标应用..."
ios launch $APP_BUNDLE --udid=$UDID

# 5. mitmproxy: 捕获流量（另开终端或后台）
echo "[*] 启动 mitmproxy 捕获..."
mitmproxy -p 8080 --mode regular -w "$OUTPUT_DIR/traffic.mitm" &
MITM_PID=$!

# 6. 配置 iOS 代理（手动或自动）
echo "[*] 请在 iOS 设备上设置 Wi-Fi 代理为: $(hostname -I | awk '{print $1}'):8080"
echo "[*] 按回车继续（已配置好代理后）..."
read

# 7. 运行 UI 自动化（触发 API 调用）
echo "[*] 运行 UI 自动化..."
# python wda_automation.py --udid $UDID

# 8. 停止 mitmproxy
echo "[*] 停止流量捕获..."
kill $MITM_PID 2>/dev/null
wait $MITM_PID 2>/dev/null

# 9. mitmproxy → HAR
echo "[*] 转换 mitmproxy 流量为 HAR..."
mitmdump -nr "$OUTPUT_DIR/traffic.mitm" -o hardump="$OUTPUT_DIR/traffic.har"

# 10. ios-traffic-intel: 解析流量
echo "[*] 解析流量情报..."
ios-traffic parse "$OUTPUT_DIR/traffic.har" \
    --goios-udid "$UDID" \
    --filter idor \
    --export-json \
    --output-dir "$OUTPUT_DIR"

# 11. Nuclei: 扫描
echo "[*] Nuclei 扫描..."
export HTTP_PROXY=http://scanner:pass@rota-server:8000
nuclei -list "$OUTPUT_DIR/nuclei_idor_targets.txt" \
       -t ~/nuclei-templates/custom/ios-*.yaml \
       -severity critical,high \
       -jsonl \
       -o "$OUTPUT_DIR/nuclei_results.jsonl"

# 12. 清理
echo "[*] 清理..."
kill $WDA_PID 2>/dev/null

echo "[+] 完成。输出: $OUTPUT_DIR"
# 可选：通过 go-ios REST API 获取设备信息，写入报告
import requests

def get_goios_devices(api_url="http://localhost:4567"):
    """获取 go-ios 管理的设备列表"""
    resp = requests.get(f"{api_url}/devices")
    return resp.json().get("deviceList", [])

# 在 TrafficAnalyzer.parse_har() 中传入 UDID
udids = [d["udid"] for d in get_goios_devices()]
report = analyzer.parse_har("traffic.har", goios_udids=udids)
