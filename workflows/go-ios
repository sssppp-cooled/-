# go_ios_driver.py
import subprocess
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class GoIOSDriver:
    """go-ios 官方 CLI 的 Python 封装 (控制面)"""
    
    # 建议将 go-ios 二进制文件放在项目的 bin 目录下，避免环境污染
    BIN = "./bin/ios" 

    def _run(self, *args, udid: str = None, timeout=60) -> str:
        cmd = [self.BIN]
        if udid:
            cmd.extend(["--udid", udid])
        cmd.extend(args)
        
        logger.debug(f"Executing: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"go-ios failed: {e.stderr}")
            raise RuntimeError(f"go-ios error: {e.stderr}")

    # --- 核心赏金功能封装 ---

    def start_tunnel(self, udid: str) -> subprocess.Popen:
        """启动 iOS 17+ 隧道 (后台常驻)"""
        return subprocess.Popen([self.BIN, "tunnel", "start", "--udid", udid], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def inject_proxyhat(self, udid: str, host: str, port: int, user: str, password: str):
        """杀手锏：一键将 ProxyHat 代理注入 iPhone 全局网络"""
        # 注意：具体参数需参考 `ios httpproxy --help`，这里为逻辑演示
        # 通常 httpproxy 会生成一个 profile 并安装到设备
        self._run("httpproxy", host, str(port), user, password, udid=udid)
        logger.info(f"[+] ProxyHat 代理已注入设备 {udid}")

    def remove_proxy(self, udid: str):
        """移除代理配置"""
        self._run("httpproxy", "remove", udid=udid)

    def run_wda(self, udid: str) -> subprocess.Popen:
        """免 Xcode 启动 WebDriverAgent"""
        # 假设 WDA 的 bundle id 已经配置好
        return subprocess.Popen([self.BIN, "runwda", "--udid", udid],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def extract_crashes(self, udid: str, output_dir: str) -> list:
        """提取 App 崩溃日志 (用于 Fuzzing 反馈)"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        # 列出并拷贝 crash 文件
        self._run("crash", "cp", output_dir, udid=udid)
        return list(Path(output_dir).glob("*.ips")) + list(Path(output_dir).glob("*.crash"))

    def get_hardware_fingerprint(self, udid: str) -> dict:
        """提取底层硬件指纹 (防关联/设备管理)"""
        # 查询关键的 MobileGestalt 键
        keys = ["SerialNumber", "WiFiAddress", "BluetoothAddress", "UniqueChipID"]
        # 实际调用需根据 `ios mobilegestalt --help` 调整
        # 这里演示解析 JSON 输出
        output = self._run("mobilegestalt", *keys, "--json", udid=udid)
        return json.loads(output)
