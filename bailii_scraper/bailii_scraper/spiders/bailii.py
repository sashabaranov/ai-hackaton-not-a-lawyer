import scrapy


class BailiiSpider(scrapy.Spider):
    name = "bailii"
    start_urls = ["https://www.bailii.org/ew/cases/EWCA/Civ/"]

    def parse(self, response):
        title = response.xpath("//title/text()").get()

        # Extract body text (simplified for this example)
        body_text = " ".join(response.xpath("//body//text()").getall()).strip()

        # Save the data as a dictionary
        yield {"url": response.url, "title": title, "body_text": body_text}

        # Follow all links on the current page
        for link in response.xpath("//a/@href").getall():
            # Construct absolute URL for relative links
            if link.startswith("/"):
                link = response.urljoin(link)
            # Follow the link and parse it
            yield scrapy.Request(link, callback=self.parse)
