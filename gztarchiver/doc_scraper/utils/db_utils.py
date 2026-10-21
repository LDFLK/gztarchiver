from datetime import datetime, timezone
from pathlib import Path
from typing import List
from gztarchiver.models import DownloadMetadata
from .file_utils import atomic_write_json

def save_metadata_to_filesystem(all_download_metadata: List[DownloadMetadata], classified_metadata_dic, config):
    merged_output = []

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    for doc in all_download_metadata:
        doc_id = doc.doc_id

        # Get classification data if available (only for available documents)
        classification = classified_metadata_dic.get(doc_id, {})

        document_file_path = Path(doc.file_path)

        # Record "N/A" for unavailable documents without mutating the input metadata
        saved_file_path = str(doc.file_path) if doc.availability == "Available" else "N/A"

        document_object = {
            "document_id": doc_id,
            "description": doc.des,
            "document_date": doc.date,
            "document_type": classification.get('doc_type', "UNAVAILABLE"),
            "categorisation": classification.get('categorisation', f"Uncategorised as of - {timestamp}."),
            "file_path": saved_file_path,
            "source": doc.download_url,
            "availability": doc.availability
        }
        
        parent_folder_of_document = document_file_path.parent
        
        document_metadata_object_path = parent_folder_of_document / f"{str(doc_id)}_metadata.json"
        
        atomic_write_json(document_metadata_object_path, document_object)
            
        print(f"Document metadata saved at : {document_metadata_object_path}")
                    
        merged_output.append(document_object)
        
    return 

