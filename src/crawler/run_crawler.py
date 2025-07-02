import asyncio
import os
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
import requests
# from pprint import pprint
from urllib.parse import urlparse
import re

OUTPUT_DIR_JSON = "data/processed/json"
OUTPUT_DIR_MD = "data/processed/markdown"

os.makedirs(OUTPUT_DIR_JSON, exist_ok=True)
os.makedirs(OUTPUT_DIR_MD, exist_ok=True)

def slugify(url):
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    path = parsed.path.strip("/").replace("/", "_")
    safe_path = re.sub(r'[^a-zA-Z0-9_-]', '', path)
    return domain + ("_" + safe_path if safe_path else "")

async def run():
    urls = [
        "https://www.theverge.com/",
        "https://news.ycombinator.com/news"
    ]

    browser_config = BrowserConfig(headless=True, verbose=True)
    run_config = CrawlerRunConfig(
        # Content filtering
        word_count_threshold=10,
        excluded_tags=['form', 'header'],
        exclude_external_links=True,
        
        # Content processing
        process_iframes=True,
        remove_overlay_elements=True,

        # Cache control
        cache_mode=None,
        # cache_mode=CacheMode.ENABLED  # Use cache if available
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for i, url in enumerate(urls, start=0):
            result = await crawler.arun(
            url=url,
            config=run_config
        )
            
            if result.success:
                # Print clean content
                print("Content:", result.markdown[:500])  # First 500 chars
                print("Links found:", len(result.links))
                print("Images found:", len(result.media["images"]))


                # # Process links
                # for link in result.links["internal"]:
                #     print(f"Internal link: {link['href']}")
                # for link in result.links["external"]:
                #     print(f"External link: {link['href']}")

                # # Process images
                # for image in result.media["images"]:
                #     print(f"Found image: {image['src']}")

                # # Save images
                # slug = slugify(url)
                # image_folder = os.path.join("data/processed/images", slug)
                # os.makedirs(image_folder, exist_ok=True)
  
                # print(f"Saving images for {url} to {image_folder}")
                # if not result.media["images"]:
                #     print("[✗] No images found.")
                #     continue
                # print(f"Found {len(result.media['images'])} images to save.")

                # # Save each image
                # for i, image in enumerate(result.media["images"], start=0):
                #     src = image.get("src")
                #     ext = os.path.splitext(src)[-1].split("?")[0]  # get extension from URL
                #     if not ext or len(ext) > 5:
                #         ext = "jpg"  # default if no extension
                #     filename = os.path.join(image_folder, f"img_{i}.{ext}")
                    
                #     try:
                #         img_data = requests.get(src).content
                #         with open(filename, "wb") as f:
                #             f.write(img_data)
                #     except Exception as e:
                #         print(f"[✗] Failed to save {url}: {e}")


                # Save JSON output (structured data)
                json_path = os.path.join(OUTPUT_DIR_JSON, f"page_{i}.json")
                with open(json_path, "w", encoding="utf-8") as f_json:
                    # pprint(result.model_dump())
                    json.dump(result.model_dump(), f_json, indent=2, ensure_ascii=False, default=str)

                # Save Markdown output
                md_path  = os.path.join(OUTPUT_DIR_MD, f"page_{i}.md")
                with open(md_path, "w", encoding="utf-8") as f_md:
                    f_md.write(result.markdown.fit_markdown)

                print(f"[✓] Saved {url} → {json_path} and {md_path}")
            
            else:
                print(f"Crawl failed for {url} : {result.error_message}")

if __name__ == "__main__":
    asyncio.run(run())

# This script runs a web crawler on specified URLs and saves the results in JSON and Markdown formats.
# It uses the crawl4ai library for asynchronous crawling and structured data handling.
# The output directories are created if they do not exist, and the results are saved with appropriate filenames.
# The script is designed to be run as a standalone program.
# It can be easily extended to include more URLs or different configurations as needed.