from doc_scraper.utils import load_years_metadata, get_year_link, hide_logs, load_doc_metadata_file, filter_doc_metadata, create_folder_structure,create_folder_structure_on_cloud, upload_local_documents_to_gdrive, filter_pdf_only, save_upload_results, get_cloud_credentials, prepare_metadata_for_db, connect_to_db, insert_docs_by_year
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
from document_scraper.document_scraper import YearsSpider
from document_scraper.document_scraper.spiders import DocMetadataSpider
from document_scraper.document_scraper.spiders import PDFDownloaderSpider
from doc_inspector.utils import extract_text_from_pdf, prepare_for_llm_processing, save_classified_doc_metadata, prepare_classified_metadata
from googleapiclient.discovery import build
import json
from pathlib import Path
from datetime import datetime

@defer.inlineCallbacks
def run_crawlers_sequentially(args, config, project_root, user_input_kind):
    """Run crawlers sequentially using CrawlerRunner"""
    
    # Hide logs (scrapy)
    settings = hide_logs()
    
    # Initiate crawling runner
    runner = CrawlerRunner(settings=settings)
    
    # Resolve paths
    output_path = project_root / config["output"]["years_json"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_path_doc_metadata = project_root / config["output"]["doc_metadata_json"]
    output_path_doc_metadata.parent.mkdir(parents=True, exist_ok=True)

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
        all_download_metadata = create_folder_structure(archive_location, filtered_doc_metadata)
                
        # Step 7: Download the documents
        if all_download_metadata:
            yield runner.crawl(PDFDownloaderSpider, download_metadata=all_download_metadata)
            print("✅ All crawlers completed successfully!")
            yield defer.maybeDeferred(post_crawl_processing, args, config, filtered_doc_metadata, archive_location)
        else:
            print("No documents to download")
            
    except Exception as e:
        print(f"Error during crawling: {e}")
    finally:
        # Continue with post-processing
        # yield defer.maybeDeferred(post_crawl_processing, args, config, filtered_doc_metadata, archive_location)
        reactor.stop()

# TODO: i have to send filtered_doc_metadata instead of the upload_metadata , otherwise if the create_folder_structure_on_cloud fails , the program stops from there.
def post_crawl_processing(args, config, filtered_doc_metadata, archive_location):
    """Handle post-crawl processing (Google Drive upload, etc.)"""
    try:
        # 🔑 Get the login credentials
        your_credentials = get_cloud_credentials(config)
        
        # Setup Google Drive API
        service = build('drive', 'v3', credentials=your_credentials)
        
        # Getting the upload metadata
        upload_metadata = create_folder_structure_on_cloud(
            service, 
            filtered_doc_metadata, 
            archive_location,
            parent_folder_id=config["archive"]["g_drive_parent_folder_id"]  
        )
                
        # Filter the available docs
        pdf_only_metadata = filter_pdf_only(upload_metadata)
                
        # Upload the docs to cloud
        results = upload_local_documents_to_gdrive(
            service, 
            pdf_only_metadata,
            max_retries=3,
            delay_between_uploads=1
        )
        
        upload_results_location = config["output"]["upload_results_json"]
        save_upload_results(results, upload_results_location)
        
        # Access specific results
        print(f"Successful uploads: {results['successful_uploads']}")
        print(f"Failed uploads: {results['failed_uploads']}")

        # Get list of successful uploads with their Google Drive file IDs
        successful_docs = [
            detail for detail in results['upload_details'] 
            if detail['status'] == 'success'
        ]

        for doc in successful_docs:
            print(f"✅ {doc['doc_id']}: {doc['gdrive_file_id']}")
            
        extracted_texts = extract_text_from_pdf(upload_metadata)
        llm_ready_texts = prepare_for_llm_processing(extracted_texts)
        
        api_key = config["credentials"]["deepseek_api_key"]
        
        classified_metadata, classified_metadata_dic = prepare_classified_metadata(llm_ready_texts, api_key)
            
        save_classified_doc_metadata(classified_metadata, archive_location, args.year)
        
        prepared_metadata_to_store = prepare_metadata_for_db(results, classified_metadata_dic)
        
        uri = config["db_credentials"]["mongo_db_uri"]
        
        client = connect_to_db(uri)
        
        if client:
            db = client["doc_db"]
            insert_docs_by_year(db, prepared_metadata_to_store, args.year)
        else:
            print("❌ Failed uploading to the mongodb")
            
    except Exception as e:
        print(f"Error during post-processing: {e}")