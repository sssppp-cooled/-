import asyncio
import yaml
from src.scraper import Scraper


# 你自己定义：怎么从页面提取数据
def my_extractor(html_content, page):
    """
    在这里写你的提取逻辑。
    返回一个 dict，会合并到结果中。
    """
    # 示例：提取页面所有文本
    # 实际使用时根据目标网站结构调整选择器
    return {
        "content_preview": html_content[:500].replace('\n', ' ')
    }


async def main():
    scraper = Scraper("config.yaml")
    
    # 示例 URL 列表（你自己替换）
    urls = [
        "https://example.com/search?q=test1",
        # ... 你的 1000 个查询
    ]
    
    for i, url in enumerate(urls, 1):
        print(f"\n📌 [{i}/{len(urls)}] 处理中...")
        result = await scraper.scrape(url, extract_fn=my_extractor)
        if result:
            scraper.results.append(result)
        
        # 批次保存
        if i % scraper.config['scraping']['batch_size'] == 0:
            scraper.save_csv(scraper.results)
        
        # 查询间大间隔
        import random
        delay = random.uniform(*scraper.config['delays']['between_queries'])
        print(f"😴 休息 {delay:.1f} 秒...")
        await asyncio.sleep(delay)
    
    # 最终保存
    scraper.save_csv(scraper.results)
    print(f"\n🏁 完成，共成功 {len(scraper.results)}/{len(urls)} 条")


if __name__ == "__main__":
    asyncio.run(main())
