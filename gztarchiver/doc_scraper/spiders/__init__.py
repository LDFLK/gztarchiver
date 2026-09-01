from gztarchiver.doc_scraper.v1.spiders.years_spider import YearsSpider
from gztarchiver.doc_scraper.v1.spiders.doc_metadata_spider import DocMetadataSpider
from gztarchiver.doc_scraper.common.spiders.doc_download_spider import PDFDownloaderSpider

__all__ = [
    "YearsSpider",
    "DocMetadataSpider",
    "PDFDownloaderSpider"
]