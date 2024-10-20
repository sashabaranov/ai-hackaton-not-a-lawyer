import asyncio
from crawl4ai import AsyncWebCrawler
from tqdm import tqdm
import json


async def main():
    urls = [
        "https://www.legislation.gov.uk/ukpga/1988/50",
        "https://www.legislation.gov.uk/ukpga/1985/70",
        "https://www.legislation.gov.uk/ukpga/2015/15",
    ]

    documents = []
    async with AsyncWebCrawler(verbose=True) as crawler:
        for url in tqdm(urls):
            result = await crawler.arun(url=url)
            documents.append({"url": url, "content": result.markdown})

    with open("data/documents_crawl4ai.json", "w") as f:
        json.dump(documents, f)


if __name__ == "__main__":
    asyncio.run(main())
