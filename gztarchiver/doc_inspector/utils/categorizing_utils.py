import requests
from gztarchiver.doc_inspector.LLM import GAZETTE_CLASSIFICATION_PROMPT
from gztarchiver.models import DownloadMetadata
from gztarchiver.doc_scraper.utils.file_utils import atomic_write_csv
from pathlib import Path
import csv
from datetime import datetime, timezone

def classify_gazette(content, doc_id, divert_api_key, divert_url):
    """
    Classifies a gazette document using DeepSeek LLM API
    
    Args:
        content (str): The gazette content to classify
        doc_id (str): Document ID for reference
        api_key (str): DeepSeek API key
        
    Returns:
        dict: Classification result with type and reasoning
    """
    
    # DeepSeek API endpoint
    url = divert_url
    
    # Construct the prompt with classification criteria
    prompt = GAZETTE_CLASSIFICATION_PROMPT.format(doc_id=doc_id, content=content)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {divert_api_key}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1
    }
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    try:
        # Make the API request
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        llm_response = result['choices'][0]['message']['content'].strip()
        
        # Extract type and reasoning
        lines = llm_response.split('\n')
        type_line = ""
        reasoning_line = ""
        
        for line in lines:
            if line.startswith("Type:"):
                type_line = line.replace("Type:", "").strip()
            elif line.startswith("Reasoning:"):
                reasoning_line = line.replace("Reasoning:", "").strip()
       # Determine final classification
        if "1" in type_line:
            classification_type = "ORGANISATIONAL"
        elif "2" in type_line:
            classification_type = "PEOPLE"
        elif "3" in type_line:
            classification_type = "HYBRID"
        elif "4" in type_line:
            classification_type = "LAND"
        elif "5" in type_line:
            classification_type = "LEGAL_REGULATORY"
        elif "6" in type_line:
            classification_type = "COMMERCIAL"
        elif "7" in type_line:
            classification_type = "ELECTIONS"
        elif "8" in type_line:
            classification_type = "PUBLIC_SERVICE"
        elif "9" in type_line:
            classification_type = "JUDICIAL_LAW_ENFORCEMENT"
        elif "10" in type_line:
            classification_type = "MISCELLANEOUS"
        else:
            classification_type = "MISCELLANEOUS"
        
        return {
            "document_id": doc_id,
            "type": classification_type,
            "categorisation": reasoning_line if reasoning_line else llm_response,
            "raw_response": llm_response,
            "success": True
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Categorization API request failed: {str(e)}")
        return {
            "document_id": doc_id,
            "type": "NOT CATEGORISED",
            "categorisation": f"Uncategorised as of - {timestamp}.",
            "raw_response": None,
            "success": False
        }
    except KeyError as e:
        print(f"Unexpected API response format: {str(e)}")
        return {
            "document_id": doc_id,
            "type": "NOT CATEGORISED",
            "categorisation": f"Uncategorised as of - {timestamp}.",
            "raw_response": response.text if 'response' in locals() else None,
            "success": False
        }
    except Exception as e:
        print(f"Unexpected error during document categorization: {str(e)}")
        return {
            "document_id": doc_id,
            "type": "NOT CATEGORISED",
            "categorisation": f"Uncategorised as of - {timestamp}.",
            "raw_response": None,
            "success": False
        }
        
def process_failed_documents(archive_location, year, config):
    error_records = []

    year_folder = Path(archive_location).expanduser() / str(year) / config["output"]["log_record_dir"]
    year_folder.mkdir(parents=True, exist_ok=True)

    csv_file_path = year_folder / config["output"]["log_classification_failed"]

    if not csv_file_path.exists():
        print(f"Skipping: {csv_file_path} does not exist yet.")
        return []

    # 1. Read all records from the failed classification log.
    # The file is not cleared here; save_classified_doc_metadata moves each
    # record to the success log once it is classified successfully.
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Document ID'):
                error_records.append(row)

    # 2. Process the identified records
    results = []
    if not error_records:
        print("No error records found to process.")
        return results
         
    for record in error_records:
        file_path_value = record.get('Document Path') or ""
        document_object = DownloadMetadata(
            doc_id=record.get('Document ID') or "",
            date=record.get('Document Date') or "",
            file_path=Path(file_path_value),
            file_name=Path(file_path_value).name,
            availability=record.get('Document Availability') or "",
            download_url=record.get('Download URL') or "",
            des=record.get('Document Description'),
        )
        results.append(document_object)
        
    return results
        
def save_classified_doc_metadata(metadata_list_success, metadata_list_failed, archive_location, year, config):
    
    year_folder = Path(archive_location).expanduser() / str(year) / config["output"]["log_record_dir"]
    year_folder.mkdir(parents=True, exist_ok=True)
    
    # Set the CSV file path
    csv_file_path_success = year_folder / config["output"]["log_classification_success"]
    csv_file_path_failed = year_folder / config["output"]["log_classification_failed"]
    header = ["Document ID", "Document Date", "Classification Type", "Categorisation", "Document Path", "Document Availability", "Download URL", "Document Description"]

    # Load existing rows keyed by Document ID
    success_rows_by_doc_id = _read_rows_by_doc_id(csv_file_path_success)
    failed_rows_by_doc_id = _read_rows_by_doc_id(csv_file_path_failed)

    # Upsert: update the row if the Document ID exists, otherwise add it.
    # Also remove it from the other log so a document lives in only one file.
    for row in metadata_list_success:
        success_rows_by_doc_id[str(row[0])] = row
        failed_rows_by_doc_id.pop(str(row[0]), None)

    for row in metadata_list_failed:
        failed_rows_by_doc_id[str(row[0])] = row
        success_rows_by_doc_id.pop(str(row[0]), None)

    # Rewrite the CSV files
    atomic_write_csv(csv_file_path_success, header, success_rows_by_doc_id.values())
    atomic_write_csv(csv_file_path_failed, header, failed_rows_by_doc_id.values())

    print(f"[✓] Metadata saved to {csv_file_path_success}")
    print(f"[✓] Metadata saved to {csv_file_path_failed}")
    return

def _read_rows_by_doc_id(csv_file_path):
    """Read a classification log CSV and return its rows keyed by Document ID."""
    rows_by_doc_id = {}
    if csv_file_path.exists():
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if row:
                    rows_by_doc_id[row[0]] = row
    return rows_by_doc_id

def prepare_classified_metadata(llm_ready_texts, divert_api_key, divert_url ):
    classified_metadata_success = []
    classified_metadata_dic_success = {}
    classified_metadata_failed = []
    classified_metadata_dic_failed = {}
        
    for doc_id in llm_ready_texts:
        doc_text = llm_ready_texts[doc_id]["text"]
        doc_date = llm_ready_texts[doc_id]["date"]
        doc_file_path = llm_ready_texts[doc_id]["file_path"]
        doc_availability = llm_ready_texts[doc_id]["availability"]
        doc_download_url = llm_ready_texts[doc_id]["download_url"]
        description = llm_ready_texts[doc_id]["des"]
        print(f"Document ID: {doc_id}")
        print(f"Document Date: {doc_date}")
        print(f"Document Path: {doc_file_path}")
        print(f"Document Availability: {doc_availability}")
        print(f"Document download URL: {doc_download_url}")
        print(f"Description: {description}")
        res = classify_gazette(doc_text, doc_id, divert_api_key, divert_url)
        doc_type = res['type']
        doc_type_reason = res['categorisation']
        if res["success"]:
            print(f"Gazette type: {res['type']}")
            print(f"Categorisation: {res['categorisation']}")
            classified_metadata, classified_metadata_dic = classified_metadata_success, classified_metadata_dic_success
        else:
            print(f"Error: {res['categorisation']}")
            classified_metadata, classified_metadata_dic = classified_metadata_failed, classified_metadata_dic_failed
        # Append metadata for later saving
        classified_metadata.append((doc_id, doc_date, doc_type, doc_type_reason, doc_file_path, doc_availability, doc_download_url, description))
        classified_metadata_dic[doc_id] = {
            'date': doc_date,
            'doc_type': doc_type,
            'categorisation': doc_type_reason,
            'file_path': doc_file_path,
            "availability": doc_availability,
            'download_url': doc_download_url,
            'des': description
        }
        print("\n" + "="*80 + "\n")
    
    return classified_metadata_success, classified_metadata_dic_success, classified_metadata_failed, classified_metadata_dic_failed