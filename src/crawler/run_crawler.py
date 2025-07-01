import asyncio
import os
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

OUTPUT_DIR_JSON = "data/processed/json"
OUTPUT_DIR_MD = "data/processed/markdown"

os.makedirs(OUTPUT_DIR_JSON, exist_ok=True)
os.makedirs(OUTPUT_DIR_MD, exist_ok=True)

async def run():
    urls = [
        "https://www.wikipedia.org",
        "https://www.example.com"
    ]

    browser_config = BrowserConfig(headless=True, verbose=True)
    run_config = CrawlerRunConfig(cache_mode=None)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for i, url in enumerate(urls, start=1):
            result = await crawler.arun(url=url)

            # Save JSON output (structured data)
            json_path = os.path.join(OUTPUT_DIR_JSON, f"page_{i}.json")
            with open(json_path, "w", encoding="utf-8") as f_json:
                json.dump(result.model_dump(), f_json, indent=2, ensure_ascii=False)

            # Save Markdown output
            md_path = os.path.join(OUTPUT_DIR_MD, f"page_{i}.md")
            with open(md_path, "w", encoding="utf-8") as f_md:
                f_md.write(result.markdown.fit_markdown)

            print(f"[✓] Saved {url} → {json_path} and {md_path}")

if __name__ == "__main__":
    asyncio.run(run())

# This script runs a web crawler on specified URLs and saves the results in JSON and Markdown formats.
# It uses the crawl4ai library for asynchronous crawling and structured data handling.
# The output directories are created if they do not exist, and the results are saved with appropriate filenames.
# The script is designed to be run as a standalone program.
# It can be easily extended to include more URLs or different configurations as needed.