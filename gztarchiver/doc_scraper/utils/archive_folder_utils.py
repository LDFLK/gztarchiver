from pathlib import Path
import json

def create_folder_structure(archive_location, filtered_doc_metadata):
    
    base_path = archive_location
    
    all_download_metadata = []
    
    for doc in filtered_doc_metadata:
        doc_id = doc.get("doc_id")
        date_str = doc.get("date")
        url = doc.get("download_url")
        availability = doc.get("availability")
        des = doc.get("description")
        
        # Parse date into year/month/day
        try:
            year, month, day = date_str.split("-")
        except ValueError:
            print(f"Skipping invalid date: {date_str}")
            continue
        
        # Build folder path: ~/Desktop/doc-archive/YYYY/MM/DD/doc_id/
        folder_path = base_path / year / month / day / doc_id
        folder_path.mkdir(parents=True, exist_ok=True)

        # Determine language from URL
        if "_E.pdf" in url:
            lang_suffix = "english"
        elif "_S.pdf" in url:
            lang_suffix = "sinhala"
        elif "_T.pdf" in url:
            lang_suffix = "tamil"
        else:
            lang_suffix = "unavailable"

        if availability != "Available" or url == "N/A":
            file_name = f"{lang_suffix}.txt"
            file_path = folder_path / file_name 
        else:      
            file_name = f"{doc_id}_{lang_suffix}.pdf"
            file_path = folder_path / file_name       
        
        download_metadata = {
            "doc_id": doc_id,
            "date": date_str,
            "des": des,
            "download_url": url,
            "file_name" : file_name,
            "file_path" : file_path,
            "availability" : availability
        }
        
        all_download_metadata.append(download_metadata)
        
        # If unavailable, save metadata to unavailable.txt
        if availability != "Available" or url == "N/A":
            unavailable_path = folder_path / "unavailable.txt"
            if unavailable_path.exists():
                print(f"⚠️  Unavailable.txt already exists: {unavailable_path}, skipping creating again")
            else:
                with open(unavailable_path, "w", encoding="utf-8") as f:
                    json.dump(doc, f, ensure_ascii=False, indent=2)
                print(f"📄 Unavailable file created: {unavailable_path}")
            continue
    
    return all_download_metadata

