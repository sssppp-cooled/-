class IOSNode:
    def __init__(self, udid: str):
        self.udid = udid
        self.ctrl = GoIOSWrapper()      # 控制面：go-ios CLI
        self.data = None                # 数据面：pymobiledevice3 (延迟初始化)

    def start(self):
        """启动节点：建隧道 -> 跑 WDA -> 转发端口"""
        # 1. 控制面：go-ios 建隧道 (iOS 17+ 必须)
        self.tunnel_proc = self.ctrl.start_tunnel(self.udid)
        time.sleep(2) # 等待隧道稳定
        
        # 2. 控制面：go-ios 跑 WDA
        self.wda_proc = self.ctrl.run_wda(
            self.udid, 
            "com.facebook.WebDriverAgentRunner.xctrunner", 
            "com.facebook.WebDriverAgentRunner.xctrunner"
        )
        time.sleep(3) # 等待 WDA 启动
        
        # 3. 控制面：转发 8100 端口给 Appium
        # (如果 go-ios forward 不好用，这里可以切到 pymobiledevice3 的 usbmux forward)
        self.ctrl.forward(self.udid, 8100, 8100)
        
        # 4. 数据面：初始化 pymobiledevice3 连接，准备抓包
        from pymobiledevice3.lockdown import create_using_usbmux
        self.lockdown = create_using_usbmux(serial=self.udid)
        
        print(f"[+] Node {self.udid} Ready (WDA @ 127.0.0.1:8100)")

    def stream_pcap(self):
        """数据面：开始抓包流"""
        from pymobiledevice3.services.pcapd import PcapdService
        return PcapdService(lockdown=self.lockdown)
