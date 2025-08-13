from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

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

            # Insert the document
            result = collection.insert_one(doc)
            print(f"📄 Inserted {doc['document_id']} into {collection_name}, ID: {result.inserted_id}")

        except Exception as e:
            print(f"❌ Failed to insert {doc['document_id']}: {e}")
    
    return

def prepare_metadata_for_db(upload_results, classified_metadata_dic):
    
    # Merge data  
    merged_output = []
    
    upload_details = upload_results["upload_details"]
        
    # Convert to lookup dictionary by doc_id
    upload_lookup = {item["doc_id"]: item for item in upload_details}
                  
    for doc_id, classification in classified_metadata_dic.items():
        upload_info = upload_lookup.get(doc_id, {})
        merged_output.append({
            "document_id": doc_id,
            "document_date": classification.get("doc_date"),
            "document_type": classification.get("doc_type"),
            "reasoning": classification.get("reasoning"),
            "gdrive_file_id": upload_info.get("gdrive_file_id"),
            "gdrive_file_url": upload_info.get("gdrive_file_url"),
            "download_url": upload_info.get("download_url")
        })
        
    return merged_output


