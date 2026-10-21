import json
from typing import List, Dict, Optional
import os

def load_doc_metadata_file(json_path: str) -> Optional[List[Dict[str, str]]]:
    if not os.path.exists(json_path):
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def filter_doc_metadata(doc_metadata, user_input_kind, year=None, month=None, date=None):
    
    if user_input_kind == "year-lang":
        status = f"{len(doc_metadata)} Documents found on {year}"
        return doc_metadata, status
    
    elif user_input_kind == "year-month-lang":
        if not year or not month:
            print("Error: year and month required for year-month-lang filtering")
            return doc_metadata
        
        target_year_month = f"{year}-{month.zfill(2)}"
        print(f"Filtering by year-month: {target_year_month}")
        
        filtered_docs = []
        
        for doc in doc_metadata:
            doc_date = doc.get('date', '')
            if doc_date.startswith(target_year_month):  # e.g., "2020-12-31" starts with "2020-12"
                filtered_docs.append(doc)
            
        if filtered_docs:
            status = f"{len(filtered_docs)} Documents found at {target_year_month}"
        else:
            status = f"No documents found at {target_year_month}"

        return filtered_docs, status
    
    elif user_input_kind == "year-month-day-lang":
        if not year or not month or not date:
            print("Error: year, month, and date required for year-month-day-lang filtering")
            return doc_metadata
        
        target_date = f"{year}-{month.zfill(2)}-{date.zfill(2)}"  # Ensure month and date are 2 digits
        print(f"Filtering by year-month-day: {target_date}")
        
        filtered_docs = []
        for doc in doc_metadata:
            doc_date = doc.get('date', '')
            if doc_date == target_date:
                filtered_docs.append(doc)
        
        if filtered_docs:
            status = f"{len(filtered_docs)} Documents found at {target_date}"
        else:
            status = f"No documents found at {target_date}"
        
        return filtered_docs, status
    
    else:
        print(f"Unknown filter kind: {user_input_kind}")
        return doc_metadata
            
    