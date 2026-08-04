import json
import time
from pathlib import Path

class DTXListener:
    """监听 go-ios dproxy 生成的 DTX 消息，寻找高危操作"""
    
    # 定义高危方法模式 (根据逆向经验积累)
    DANGEROUS_METHODS = [
        "installApp", "uninstallApp", 
        "resetNetwork", "restoreDevice",
        "setLocation", "enableDeveloperMode"
    ]

    def __init__(self, log_dir="./dtx_logs"):
        self.log_dir = Path(log_dir)
        
    def stream_events(self):
        """实时读取 JSON 日志流"""
        # 假设 go-ios 以 append 模式写入 JSON lines
        log_file = self.log_dir / "device_in.json"
        with open(log_file, 'r') as f:
            f.seek(0, 2) # 移到文件末尾
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                    
                try:
                    msg = json.loads(line)
                    self.analyze(msg)
                except json.JSONDecodeError:
                    continue

    def analyze(self, msg):
        """分析 DTX 消息"""
        if msg.get('MessageType') == 'Methodinvocation':
            method = msg.get('method', '')
            aux = msg.get('auxiliary', '')
            
            # 1. 检查是否调用了敏感私有 API
            for danger in self.DANGEROUS_METHODS:
                if danger in method:
                    print(f"[!] 发现高危 DTX 调用: {method} | 参数: {aux}")
                    
            # 2. 检查 Auxiliary 中是否有可疑的 Payload (如路径遍历)
            if '../' in aux or 'file://' in aux:
                print(f"[!] 疑似路径遍历 Payload: {aux}")

# 运行
listener = DTXListener()
listener.stream_events()
