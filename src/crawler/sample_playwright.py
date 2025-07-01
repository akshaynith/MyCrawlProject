# from playwright.sync_api import sync_playwright

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=True)
#     page = browser.new_page()
#     page.goto("https://www.nbcnews.com/business")
#     print(page.title())
#     print(page.content())
#     browser.close()

import asyncio
from playwright.async_api import async_playwright

def clean_text(text):
    return text.strip().replace('\n', ' ').replace('\r', '')

async def scrape_page(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)  # wait up to 60s

        # Wait for full rendering
        await page.wait_for_load_state("networkidle")

        # Extract content
        title = await page.title()
        h1s = await page.locator("h1").all_text_contents()
        h2s = await page.locator("h2").all_text_contents()
        h3s = await page.locator("h3").all_text_contents()
        paragraphs = await page.locator("p").all_text_contents()
        links = await page.locator("a").all()

        # Build Markdown-style output
        markdown = f"# {title}\n\n"

        for h1 in h1s:
            markdown += f"## {clean_text(h1)}\n"
        for h2 in h2s:
            markdown += f"### {clean_text(h2)}\n"
        for h3 in h3s:
            markdown += f"#### {clean_text(h3)}\n"

        markdown += "\n---\n\n"
        for p in paragraphs:
            cleaned = clean_text(p)
            if len(cleaned) > 40:  # Ignore boilerplate lines
                markdown += f"{cleaned}\n\n"

        markdown += "\n---\n\n## Links Found:\n"
        for link in links:
            try:
                href = await link.get_attribute("href")
                text = clean_text(await link.inner_text())
                if href and text:
                    markdown += f"- [{text}]({href})\n"
            except:
                continue

        await browser.close()
        return markdown

# Example usage
if __name__ == "__main__":
    url = "https://www.nbcnews.com/business"
    output_file = "output.md"

    markdown_result = asyncio.run(scrape_page(url))

    output_file = "data/processed/markdown/output.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_result)


    print(f"✅ Scraping completed and saved to {output_file}")
