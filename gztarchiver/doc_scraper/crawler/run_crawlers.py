from gztarchiver.doc_scraper.utils import load_years_metadata, get_year_link, hide_logs, load_doc_metadata_file, filter_doc_metadata, create_folder_structure, save_metadata_to_filesystem
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
from gztarchiver.document_scraper.document_scraper import YearsSpider
from gztarchiver.document_scraper.document_scraper.spiders import DocMetadataSpider
from gztarchiver.document_scraper.document_scraper.spiders import PDFDownloaderSpider
from gztarchiver.doc_inspector.utils import extract_text_from_pdf, prepare_for_llm_processing, save_classified_doc_metadata, prepare_classified_metadata, process_failed_documents
from googleapiclient.discovery import build
import json
from pathlib import Path
from datetime import datetime
import shutil
import os

@defer.inlineCallbacks
def run_crawlers_sequentially(args, config, user_input_kind):
    """Run crawlers sequentially using CrawlerRunner"""
    
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
        print("Checking for updates from the website...")    
        yield runner.crawl(YearsSpider, url=config["scrape"]["url"], output_path=str(output_path))
        print(f"Updated year metadata saved to {output_path}")
        
        # Step 2: Validate CLI --year against scraped data
        metadata = load_years_metadata(output_path)
        scraped_years = [entry["year"] for entry in metadata]
        
        if str(args.year) not in scraped_years:
            print(f"Error: Year '{args.year}' is not available in scraped data.")
            print(f"Available years: {', '.join(scraped_years)}")
            reactor.stop()
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
            reactor.stop()
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
        ARCHIHVE_LOCATION = Path(archive_location)
        all_download_metadata = create_folder_structure(ARCHIHVE_LOCATION, filtered_doc_metadata)
                        
        # Step 7: Download the documents
        if all_download_metadata:
            output_path_download = config["output"]["download_metadata_json"]
            OUTPUT_PATH_DOWNLOAD = Path(output_path_download)
            OUTPUT_PATH_DOWNLOAD.parent.mkdir(parents=True, exist_ok=True)
            
            yield runner.crawl(PDFDownloaderSpider, download_metadata=all_download_metadata, output_path=str(output_path_download))
            print("✅ All crawlers completed successfully!")
                        
            updated_all_download_metadata = load_doc_metadata_file(output_path_download)
            
            if updated_all_download_metadata:
                yield defer.maybeDeferred(post_crawl_processing, args, config, updated_all_download_metadata, archive_location)
            else:
                yield defer.maybeDeferred(post_crawl_processing, args, config, all_download_metadata, archive_location)
        else:
            print("No documents to download")
            
    except Exception as e:
        print(f"Error during crawling: {e}")
    finally:
        # Continue with post-processing
        reactor.stop()

# TODO: i have to send filtered_doc_metadata instead of the upload_metadata , otherwise if the create_folder_structure_on_cloud fails , the program stops from there.
def post_crawl_processing(args, config, all_download_metadata, archive_location):
    """Handle post-crawl processing (Data preprocessing, etc.)"""
    try:
     
        # check for the existing classified metdata logs
        results = process_failed_documents(archive_location, args.year)
        
        total_documents_to_process = all_download_metadata + results
        # Extract data from the pdf files    
        extracted_texts = extract_text_from_pdf(total_documents_to_process)
        
        # Preprocess the extracted data to be used on LLM
        llm_ready_texts = prepare_for_llm_processing(extracted_texts)
        
        divert_api_key = config["credentials"]["divert_deepseek_api_key"]
        divert_url = config["credentials"]["divert_url_deep_seek"]
        
        # Classification process of the pdfs'
        classified_metadata, classified_metadata_dic = prepare_classified_metadata(llm_ready_texts, divert_api_key, divert_url)
        print(f"{'-' * 80}")
       
        # TODO : data is not relaiable, issue when saving, rewrite the whole file again in the next run   
        # Saving the classified metadata of the pdfs'

        
        save_classified_doc_metadata(classified_metadata, archive_location, args.year)
        
      
        # Processing metadata to save
        save_metadata_to_filesystem(total_documents_to_process, classified_metadata_dic, config)
        
        # Establish db connection and upload process        
        # uri = config["db_credentials"]["mongo_db_uri"]
        
        # client = connect_to_db(uri)
        
        # # TODO : update the schema of the backend for CRUD
        # if client:
        #     db = client["doc_db"]
        #     insert_docs_by_year(db, prepared_metadata_to_store, args.year)
        # else:
        #     print("❌ Failed uploading to the mongodb")
        
        # clear the temp metadata dir used by the program
        temp_metadata_dir_path = config["output"]["metadata_dir"]
               
        if os.path.exists(temp_metadata_dir_path) and os.path.isdir(temp_metadata_dir_path):
            shutil.rmtree(temp_metadata_dir_path)
            print("Cleared the temp metadata directory")
        else:
            print("Temp metadata directory not exists")
        
    except Exception as e:
        print(f"Error during post-processing: {e}")