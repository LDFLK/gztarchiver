from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from pathlib import Path
import json

def connect_to_db(mongo_uri):
    try:
        client = MongoClient(mongo_uri)
        
        # Attempt to connect to the server
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully.")

        return client

    except ConnectionFailure as e:
        print("❌ Failed to connect to MongoDB:", e)
        return None

def insert_docs_by_year(db, prepared_metadata_to_store, year):
    for doc in prepared_metadata_to_store:
        try:
            # Extract year from the document_date
            collection_name = f"gazettes_{year}"
            collection = db[collection_name]

            # Check if document already exists in the collection
            existing_doc = collection.find_one({"document_id": doc['document_id']})
            
            if existing_doc:
                # Update the existing document with new data
                result = collection.update_one(
                    {"document_id": doc['document_id']},
                    {"$set": doc}
                )
                print(f"🔄 Updated {doc['document_id']} in {collection_name}, matched: {result.matched_count}")
            else:
                # Insert the document if it doesn't exist
                result = collection.insert_one(doc)
                print(f"📄 Inserted {doc['document_id']} into {collection_name}, ID: {result.inserted_id}")

        except Exception as e:
            print(f"❌ Failed to insert/update {doc['document_id']}: {e}")
    
    return

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

