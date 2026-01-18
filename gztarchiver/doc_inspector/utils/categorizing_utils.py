import requests
from gztarchiver.doc_inspector.LLM import GAZETTE_CLASSIFICATION_PROMPT
from pathlib import Path
import csv

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
            "reasoning": reasoning_line if reasoning_line else llm_response,
            "raw_response": llm_response,
            "success": True
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "document_id": doc_id,
            "type": "NOT CATEGORISED",
            "reasoning": f"API request failed: {str(e)}",
            "raw_response": None,
            "success": False
        }
    except KeyError as e:
        return {
            "document_id": doc_id,
            "type": "NOT CATEGORISED",
            "reasoning": f"Unexpected API response format: {str(e)}",
            "raw_response": response.text if 'response' in locals() else None,
            "success": False
        }
    except Exception as e:
        return {
            "document_id": doc_id,
            "type": "NOT CATEGORISED",
            "reasoning": f"Unexpected error: {str(e)}",
            "raw_response": None,
            "success": False
        }
        
def process_failed_documents(archive_location, year):
    error_records = []
    kept_rows = []
    
    year_folder = Path(archive_location).expanduser() / str(year)
    year_folder.mkdir(parents=True, exist_ok=True)
    
    csv_file_path = year_folder / "classified_metadata.csv"
    
    if not csv_file_path.exists():
        print(f"Skipping: {csv_file_path} does not exist yet.")
        return []
    
    # open the csv and check for the Gazette Type == 'Error' records.
    # Then process them one time again and get the result
    
    # 1. Open and read the CSV to find 'Error' records
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            # Check if the Gazette Type column matches 'Error'
            if row.get('Gazette Type') == 'Error':
                error_records.append(row)
            else:
                kept_rows.append(row)
                
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept_rows)
                
    # 2. Process the identified records
    results = []
    if not error_records:
        print("No error records found to process.")
        return results
         
    for record in error_records:
        file_path_value = record.get('Document Path')
        document_object = {
            "doc_id": record.get('Document ID'),
            "date": record.get('Document Date'),
            "file_path": record.get('Document Path'),
            "file_name": Path(file_path_value).name if file_path_value else None,
            "availability": record.get('Document Availability'),
            "download_url": record.get('Download URL'),
            "des": record.get('Document Description')
        }
        results.append(document_object)
        
    return results
    
    
        
def save_classified_doc_metadata(metadata_list, archive_location, year):
    
    year_folder = Path(archive_location).expanduser() / str(year)
    year_folder.mkdir(parents=True, exist_ok=True)
    
    # Set the CSV file path
    csv_file_path = year_folder / "classified_metadata.csv"
    file_exists = csv_file_path.exists()
    
    # Write or append to the CSV file
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Document ID", "Document Date", "Gazette Type", "Reasoning", "Document Path", "Document Availability", "Download URL", "Document Description"])
        for row in metadata_list:
            writer.writerow(row)

    print(f"[✓] Metadata saved to {csv_file_path}")
        
    return


# def save_classified_doc_metadata(metadata_list, archive_location, year):
#     """
#     csv_file_path: Path to the CSV file
#     new_records: A list of dictionaries containing the new metadata
#     """
#     year_folder = Path(archive_location).expanduser() / str(year)
#     year_folder.mkdir(parents=True, exist_ok=True)
    
#      # Set the CSV file path
#     csv_file_path = year_folder / "classified_metadata.csv"
    
#     # 1. Define the exact columns you have
#     fieldnames = [
#         "Document ID", 
#         "Document Date", 
#         "Gazette Type", 
#         "Reasoning", 
#         "Document Path", 
#         "Document Availability", 
#         "Download URL", 
#         "Document Description"
#     ]
    
#     existing_data = {}

#     # 2. Read existing records into memory to check for duplicates
#     if csv_file_path.exists():
#         with open(csv_file_path, mode='r', newline='', encoding='utf-8') as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 doc_id = row.get("Document ID")
#                 if doc_id:
#                     # Store existing row using ID as key
#                     existing_data[doc_id] = row

#     # 3. Update or Add new records
#     for record in metadata_list:
#         doc_id = record.get("Document ID")
#         if doc_id:
#             # This replaces the old record with the same ID or adds a new one
#             existing_data[doc_id] = record

#     # 4. Write the merged data back to the CSV
#     # We use 'w' to overwrite the file with the updated unique set of records
#     with open(csv_file_path, mode='w', newline='', encoding='utf-8') as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(existing_data.values())

#     print(f"Metadata updated successfully in {csv_file_path}")


def prepare_classified_metadata(llm_ready_texts, divert_api_key, divert_url ):
    classified_metadata = []
    classified_metadata_dic = {}
        
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
        if res["success"]:
            doc_type = res['type']
            doc_type_reason = res['reasoning']
            print(f"Gazette type: {res['type']}")
            print(f"Reasoning: {res['reasoning']}")
        else:
            doc_type = "Error"
            doc_type_reason = res['reasoning']
            print(f"Error: {res['reasoning']}")
        # Append metadata for later saving
        classified_metadata.append((doc_id, doc_date, doc_type, doc_type_reason, doc_file_path, doc_availability, doc_download_url, description))
        classified_metadata_dic[doc_id] = {
            'date': doc_date,
            'doc_type': doc_type,
            'reasoning': doc_type_reason,
            'file_path': doc_file_path,
            "availability": doc_availability,
            'download_url': doc_download_url,
            'des': description
        }
        print("\n" + "="*80 + "\n") 
    
    return classified_metadata, classified_metadata_dic