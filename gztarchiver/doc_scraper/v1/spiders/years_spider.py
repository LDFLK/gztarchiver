import scrapy
import os
from urllib.parse import urljoin
from gztarchiver.doc_scraper.utils.file_utils import atomic_write_json

class YearsSpider(scrapy.Spider):
    name = "years"

    def __init__(self, url, output_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.output_path = os.path.expanduser(output_path)

    def parse(self, response):
        data = []
        for a in response.css("div.button-container a.btn"):
            year = a.css("::text").get()
            href = a.css("::attr(href)").get()
            full_url = urljoin(response.url, href)  # join base URL + relative path
            data.append({"year": year, "link": full_url})

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        atomic_write_json(self.output_path, data)

        self.log(f"Saved {len(data)} year links to {self.output_path}")
