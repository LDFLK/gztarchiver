from pathlib import Path
import json

def save_metadata_to_filesystem(all_download_metadata, classified_metadata_dic, config):
    merged_output = []
    
    ARCHIVE_BASE_URL = config["archive"]["archive_base_url"]
    FORCE_DOWNLOAD_BASE_URL = config["archive"]["force_download_base_url"]
    
    
    for doc in all_download_metadata:
        doc_id = doc['doc_id']
        
        # Get classification data if available (only for available documents)
        classification = classified_metadata_dic.get(doc_id, {})
        
        download_url = (
            doc['download_url']
            if doc['download_url'] == 'N/A'
            else FORCE_DOWNLOAD_BASE_URL + str(doc['file_path']).lstrip("/")
        )
        
        document_object = {
            "document_id": doc_id,
            "description": doc['des'],
            "document_date": doc['date'],
            "document_type": classification.get('doc_type', "UNAVAILABLE"),
            "reasoning": classification.get('reasoning', "NOT-FOUND"),
            "file_path": ARCHIVE_BASE_URL + str(doc['file_path']).lstrip("/"),
            "download_url": download_url,
            "source": doc['download_url'],
            "availability": doc['availability']   
        }
        
        document_file_path = Path(doc["file_path"])
        
        parent_folder_of_document = document_file_path.parent
        
        document_metadata_object_path = parent_folder_of_document / f"{str(doc_id)}_metadata.json"
        
        with open(document_metadata_object_path, "w") as f:
            json.dump(document_object, f, indent=2)
            
        print(f"Document metadata saved at : {document_metadata_object_path}")
                    
        merged_output.append(document_object)
        
    return 

