from gztarchiver.doc_scraper.utils import (
    load_years_metadata,
    get_year_link,
    hide_logs,
    load_doc_metadata_file,
    filter_doc_metadata,
    create_folder_structure,
)
from scrapy.crawler import CrawlerRunner
from twisted.internet import defer
from pathlib import Path
from gztarchiver.doc_scraper.v1.spiders import YearsSpider, DocMetadataSpider
from gztarchiver.doc_scraper.common.spiders import PDFDownloaderSpider
from gztarchiver.doc_scraper.common.post_processing import post_crawl_processing

@defer.inlineCallbacks
def run_v1_pipeline(args, config, user_input_kind):
    """Run V1 legacy crawlers sequentially using CrawlerRunner"""
    
    # Hide logs (scrapy)
    settings = hide_logs()
    
    # Initiate crawling runner
    runner = CrawlerRunner(settings=settings)
    
    # Resolve paths
    output_path = config["output"]["years_json"]
    OUTPUT_PATH = Path(output_path)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    output_path_doc_metadata = config["output"]["doc_metadata_json"]
    OUTPUT_PATH_DOC_METADATA = Path(output_path_doc_metadata)
    OUTPUT_PATH_DOC_METADATA.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Step 1: Scrape latest year links and save to years.json
        print("Checking for updates from the website (V1)...")    
        yield runner.crawl(YearsSpider, url=config["scrape"]["url"], output_path=str(output_path))
        print(f"Updated year metadata saved to {output_path}")
        
        # Step 2: Validate CLI --year against scraped data
        metadata = load_years_metadata(output_path)
        scraped_years = [entry["year"] for entry in metadata]
        
        if str(args.year) not in scraped_years:
            print(f"Error: Year '{args.year}' is not available in scraped data.")
            print(f"Available years: {', '.join(scraped_years)}")
            return

        # Step 3: Continue processing with valid input
        print(f"✅ Year '{args.year}' is valid.")
        print(f"Parameters: year={args.year}, month={args.month}, day={args.day}, lang={args.lang}")
        
        # Get the URL corresponding to the relevant year
        year_url = get_year_link(args.year, metadata)
        
        if year_url:
            print(f"✅ Year link: {year_url}")
        else:
            print("❌ Year not found in metadata.")
            return
            
        # Step 4: Scrape the table metadata for the relevant year URL
        yield runner.crawl(DocMetadataSpider, url=year_url, lang=str(args.lang), output_path=str(output_path_doc_metadata))
        
        # Step 5: Filter the metadata based on the input kind
        doc_metadata = load_doc_metadata_file(output_path_doc_metadata)

        filtered_doc_metadata, status = filter_doc_metadata(
            doc_metadata, 
            user_input_kind, 
            year=str(args.year), 
            month=str(args.month),
            date=str(args.day)
        )
        
        print(f"Status : {status}")
        
        # Step 6: Create the folder structure for the filtered data and get download metadata
        archive_location = config["archive"]["archive_location"]
        ARCHIVE_LOCATION = Path(archive_location)
        all_download_metadata = create_folder_structure(ARCHIVE_LOCATION, filtered_doc_metadata)
                        
        # Step 7: Download the documents
        if all_download_metadata:
            output_path_download = config["output"]["download_metadata_json"]
            OUTPUT_PATH_DOWNLOAD = Path(output_path_download)
            OUTPUT_PATH_DOWNLOAD.parent.mkdir(parents=True, exist_ok=True)
            
            yield runner.crawl(PDFDownloaderSpider, download_metadata=all_download_metadata, output_path=str(output_path_download), config=config)
            print("✅ All crawlers completed successfully!")
                        
            updated_all_download_metadata = load_doc_metadata_file(output_path_download)
            
            if updated_all_download_metadata:
                yield defer.maybeDeferred(post_crawl_processing, args, config, updated_all_download_metadata, archive_location)
            else:
                yield defer.maybeDeferred(post_crawl_processing, args, config, all_download_metadata, archive_location)
        else:
            print("No documents to download")
            
    except Exception as e:
        print(f"Error during V1 crawling: {e}")
