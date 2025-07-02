import asyncio
import os
import json
from unittest import result
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

# Output path
OUTPUT_DIR = "data/processed/ollama"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Define structured schema (match fields exactly!)
class ArticleInfo(BaseModel):
    title: str | None = Field(None, description="Title of the article")
    author: str | None = Field(None, description="Author of the article")
    date: str | None = Field(None, description="Publish date")

# 2. Async crawl + extract function
async def run():
    url = "https://blog.google/technology/ai/google-gemini-ai/"

    extraction_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(provider="ollama/mistral"),
        schema=ArticleInfo.model_json_schema(),  #  Updated from `.schema()` to `.model_json_schema()`
        extraction_type="schema",
        instruction="""
You are an API extractor.

Given a page describing an article, extract the following fields into a single JSON object:

{
  "title": "<title of the article>",
  "author": "<author's name>",
  "date": "<published date of the article>"
}

Rules:
- Only output valid JSON.
- Do not include explanations or comments.
- Do not return lists or arrays.
- Do not invent data — if not found, return null.
""",
        force_json_response=True
        # temperature=0.2,
        # top_p=0.9,
    )

    # 3. Optional deep crawl (set depth and max pages as needed)
    deep_strategy = BFSDeepCrawlStrategy(
        max_depth=1,
        include_external=False,
        max_pages=1,
    )

    config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        deep_crawl_strategy=deep_strategy,
        word_count_threshold=50,
        verbose=True,
    )

    async with AsyncWebCrawler(verbose=True) as crawler:
        results = await crawler.arun(url=url, config=config)

        if not isinstance(results, list):
            results = [results]

        for i, result in enumerate(results, start=1):
            if result.success:
                try:
                    # Expecting a single object, not an array
                    print("Raw Extracted Content:")
                    print(result.extracted_content)
                    data = json.loads(result.extracted_content)
                    path = os.path.join(OUTPUT_DIR, f"page_{i}.json")
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"[✓] Saved: {result.url} → {path}")
                except Exception as e:
                    print(f"[✗] JSON decode failed for {result.url}: {e}")
                    print("Raw content:\n", result.extracted_content)
            else:
                print(f"[✗] Crawl failed: {result.url}: {result.error_message}")

# 4. Entrypoint
if __name__ == "__main__":
    asyncio.run(run())
