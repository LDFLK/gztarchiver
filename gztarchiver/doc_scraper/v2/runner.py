from pathlib import Path
from twisted.internet import defer
from scrapy.crawler import CrawlerRunner
from gztarchiver.doc_scraper.utils import (
    hide_logs,
    create_folder_structure,
    load_doc_metadata_file,
)
from gztarchiver.doc_scraper.common.spiders import PDFDownloaderSpider
from gztarchiver.doc_scraper.common.post_processing import post_crawl_processing
from gztarchiver.doc_scraper.v2.api_client import fetch_gazette_metadata_v2

@defer.inlineCallbacks
def run_v2_pipeline(args, config, user_input_kind):
    """Run V2 crawler pipeline (API retrieval / V2 Spiders + Downloader)"""
    try:
        print("Starting V2 Crawler Pipeline...")
        
        # Step 1: Fetch normalized document metadata from V2 API / Source
        filtered_doc_metadata = yield defer.maybeDeferred(fetch_gazette_metadata_v2, args, config)
        
        if not filtered_doc_metadata:
            print("No documents found for the given criteria (or V2 fetch logic not yet implemented).")
            return
            
        # Step 2: Create local folder structure and prepare download metadata
        archive_location = config["archive"]["archive_location"]
        ARCHIVE_LOCATION = Path(archive_location)
        all_download_metadata = create_folder_structure(ARCHIVE_LOCATION, filtered_doc_metadata)
        
        # Step 3: Download documents
        if all_download_metadata:
            output_path_download = config["output"]["download_metadata_json"]
            OUTPUT_PATH_DOWNLOAD = Path(output_path_download)
            OUTPUT_PATH_DOWNLOAD.parent.mkdir(parents=True, exist_ok=True)
            
            settings = hide_logs()
            runner = CrawlerRunner(settings=settings)
            
            yield runner.crawl(
                PDFDownloaderSpider, 
                download_metadata=all_download_metadata, 
                output_path=str(output_path_download), 
                config=config
            )
            print("✅ V2 Crawler download completed successfully!")
            
            updated_all_download_metadata = load_doc_metadata_file(output_path_download)
            
            # Step 4: Post-crawl processing (LLM text extraction, classification, filesystem saving)
            if updated_all_download_metadata:
                yield defer.maybeDeferred(post_crawl_processing, args, config, updated_all_download_metadata, archive_location)
            else:
                yield defer.maybeDeferred(post_crawl_processing, args, config, all_download_metadata, archive_location)
        else:
            print("No documents to download.")
            
    except Exception as e:
        print(f"Error during V2 crawling: {e}")
