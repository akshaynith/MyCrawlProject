import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def run():
    urls = [
        "https://www.example.com",
        "https://en.wikipedia.org/wiki/United_States_strikes_on_Iranian_nuclear_sites"
    ]

    browser_config = BrowserConfig(headless=True, verbose=True)
    run_config = CrawlerRunConfig(cache_mode=None)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            result = await crawler.arun(url=url)
            print(f"[+] Fetched from {url}")
            print(result.markdown.fit_markdown)  # or save it to a file

if __name__ == "__main__":
    asyncio.run(run())
