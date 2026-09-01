import os
import shutil
from pathlib import Path
from gztarchiver.doc_inspector.utils import (
    extract_text_from_pdf,
    prepare_for_llm_processing,
    save_classified_doc_metadata,
    prepare_classified_metadata,
    process_failed_documents,
)
from gztarchiver.doc_scraper.utils import save_metadata_to_filesystem

# TODO: i have to send filtered_doc_metadata instead of the upload_metadata , otherwise if the create_folder_structure_on_cloud fails , the program stops from there.
def post_crawl_processing(args, config, all_download_metadata, archive_location):
    """Handle post-crawl processing (Data preprocessing, etc.)"""
    try:
        classified_metadata_dic = {}
        total_documents_to_process = all_download_metadata

        # Check if classification is enabled in config (defaults to True)
        classification_enabled = config.get("classification", {}).get("enable", True)

        if classification_enabled:
            # check for the existing classified metadata logs
            results = process_failed_documents(archive_location, args.year, config)
            
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
           
            # TODO : data is not reliable, issue when saving, rewrite the whole file again in the next run   
            # Saving the classified metadata of the pdfs'
            save_classified_doc_metadata(classified_metadata, archive_location, args.year, config)
        else:
            print("\nDocument classification is disabled in configuration. Skipping LLM processing.\n")
      
        # Processing metadata to save
        save_metadata_to_filesystem(total_documents_to_process, classified_metadata_dic, config)
        
        # clear the temp metadata dir used by the program
        temp_metadata_dir_path = config["output"]["metadata_dir"]
               
        if os.path.exists(temp_metadata_dir_path) and os.path.isdir(temp_metadata_dir_path):
            shutil.rmtree(temp_metadata_dir_path)
            print("Cleared the temp metadata directory")
        else:
            print("Temp metadata directory not exists")
        
    except Exception as e:
        print(f"Error during post-processing: {e}")
        raise
