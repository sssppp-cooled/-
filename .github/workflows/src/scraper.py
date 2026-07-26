import asyncio
import csv
import os
import yaml
from datetime import datetime

import nodriver as nd

from .proxy_pool import ProxyPool
from .human_behavior import human_delay, human_scroll
from .error_handler import ErrorHandler, BlockType


class Scraper:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.pool = ProxyPool.from_json(
            self.config['proxy']['proxy_file'],
            self.config['proxy']['max_fail'],
            self.config['proxy']['cooldown_minutes']
        )
        self.error_handler = ErrorHandler(self.pool)
        self.results = []
        os.makedirs("data", exist_ok=True)
    
    async def _create_browser(self, proxy):
        browser_args = [
            f'--proxy-server={proxy.url}',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            f'--window-size={self.config["browser"]["window_size"]}',
            f'--lang={self.config["browser"]["lang"]}',
            f'--timezone={self.config["browser"]["timezone"]}',
        ]
        
        browser = await nd.start(
            headless=self.config['browser']['headless'],
            browser_args=browser_args
        )
        return browser
    
    async def scrape(self, url: str, extract_fn=None) -> dict:
        proxy = self.pool.get_proxy()
        browser = None
        
        for attempt in range(self.config['scraping']['max_retries']):
            try:
                print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] 尝试 {attempt+1} | 代理: {proxy.host} | URL: {url[:60]}...")
                
                browser = await self._create_browser(proxy)
                page = await browser.get(url)
                
                # 等 Cloudflare 挑战
                await human_delay(*self.config['delays']['page_load'])
                
                content = await page.get_content()
                title = await page.evaluate("document.title")
                
                # 检查封锁
                block_type = self.error_handler.detect(content)
                if block_type != BlockType.UNKNOWN:
                    raise Exception(f"检测到封锁: {block_type.value}")
                
                # 模拟人类阅读
                await human_scroll(page)
                await human_delay(*self.config['delays']['post_search_read'])
                
                # 提取数据（由调用方提供函数，或返回原始内容）
                data = {"url": url, "title": title, "html": content, "timestamp": datetime.now().isoformat()}
                if extract_fn:
                    data.update(extract_fn(content, page))
                
                self.pool.report(proxy, True)
                print(f"✅ 成功")
                return data
                
            except Exception as e:
                print(f"❌ 失败: {e}")
                self.pool.report(proxy, False)
                
                if browser:
                    await browser.stop()
                    browser = None
                    await asyncio.sleep(2)
                
                if attempt < self.config['scraping']['max_retries'] - 1:
                    backoff = self.error_handler.handle(proxy, self.error_handler.detect(str(e)), attempt)
                    print(f"⏳ 退避 {backoff:.1f} 秒...")
                    await asyncio.sleep(backoff)
                    proxy = self.pool.get_proxy()
                else:
                    print(f"💀 彻底放弃: {url}")
                    return None
            
            finally:
                if browser:
                    await browser.stop()
                    await asyncio.sleep(3)
        
        return None
    
    def save_csv(self, data_list: list):
        if not data_list:
            return
        keys = set()
        for d in data_list:
            keys.update(d.keys())
        keys = sorted(keys)
        
        filepath = self.config['scraping']['output_file']
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data_list)
        print(f"💾 已保存 {len(data_list)} 条到 {filepath}")
