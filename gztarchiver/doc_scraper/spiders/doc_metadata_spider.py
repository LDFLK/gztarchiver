import scrapy
from urllib.parse import urljoin
import os
import json

class DocMetadataSpider(scrapy.Spider):
    name = "doc_metadata_spider"

    def __init__(self, url=None, lang=None,output_path=None, **kwargs):
        self.start_urls = [url]
        self.lang = lang.lower()
        self.output_path = output_path
        super().__init__(**kwargs)

    def parse(self, response):
        all_table_metadata = []
    
        lang_map = {
            "en": ("English", "btn-primary"),
            "si": ("Sinhala", "btn-secondary"),
            "ta": ("Tamil", "btn-success")
        }

        lang_label, lang_class = lang_map.get(self.lang, ("English", "btn-primary"))

        rows = response.css("table.table-bordered tbody tr")
        for row in rows:
            gazette_number = row.css("td:nth-child(1)::text").get().strip()
            gazette_date = row.css("td:nth-child(2)::text").get().strip()
            description = row.css("td:nth-child(3)::text").get().strip()
            
            doc_id = gazette_number.replace('/', '-')
            availability = "Unavailable"
            download_url = "N/A"

            download_td = row.css("td:nth-child(4)")
            lang_button = download_td.css(f"a:has(button.{lang_class})")

            if lang_button:
                href = lang_button.css("::attr(href)").get()
                if href:
                    download_url = urljoin(response.url, href)
                    availability = "Available"
                    
            table_metadata = {
                "doc_id": doc_id,
                "date": gazette_date,
                "description": description,
                "download_url": download_url,
                "availability": availability
            }
            
            all_table_metadata.append(table_metadata)
        # TODO: This function should consider
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(all_table_metadata, f, indent=2)
        print("Data saved to doc_metadata.json") 


        
