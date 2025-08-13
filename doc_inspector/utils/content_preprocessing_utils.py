import PyPDF2
import re
from pathlib import Path
from typing import List, Dict, Any
import unicodedata

def clean_extracted_text(text: str) -> str:
    """
    Clean and format extracted PDF text for LLM processing.
    
    Args:
        text: Raw extracted text from PDF
        
    Returns:
        Cleaned and formatted text
    """
    if not text:
        return ""
    
    # Remove page separators and markers
    text = re.sub(r'\n--- Page \d+ ---\n', '\n\n', text)
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Multiple newlines to double newline
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Remove empty lines at the beginning and end
    text = text.strip()
    
    # Remove non-printable characters except common ones
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
    
    # Fix common OCR/PDF extraction issues
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between lowercase and uppercase
    text = re.sub(r'(\d)([A-Z])', r'\1 \2', text)  # Add space between digit and uppercase
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)  # Add space after sentence punctuation
    
    # Remove decorative separators
    text = re.sub(r'[─-]{3,}', '', text)  # Remove separator lines
    text = re.sub(r'[=]{3,}', '', text)   # Remove equal sign separators
    
    # Clean up excessive spaces again after processing
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n +', '\n', text)
    text = re.sub(r' +\n', '\n', text)
    
    return text.strip()


def extract_text_from_pdf(upload_metadata: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Extract and clean text from PDF documents based on upload metadata.
    
    Args:
        upload_metadata: List of dictionaries containing document metadata
        
    Returns:
        Dictionary with doc_id as key and cleaned extracted text as value
    """
    extracted_texts = {}
    
    print("\n" + "=" * 80)
    print("DOCUMENT TEXT EXTRACTION PROCESS")
    print("=" * 80)
    
    for doc_info in upload_metadata:
        doc_id = doc_info['doc_id']
        doc_date = doc_info['doc_date']
        file_name = doc_info['file_name']
        availability = doc_info['availability']
        local_path = Path(doc_info['local_path'])
        
        print(f"\n{'─' * 60}")
        print(f"Processing Document ID: {doc_id}")
        print(f"Document Date: {doc_date}")
        print(f"File Name: {file_name}")
        print(f"Availability: {availability}")
        print(f"Local Path: {local_path}")
        print(f"{'─' * 60}")
        
        # Skip unavailable documents
        if availability == 'Unavailable' or file_name == 'unavailable.json':
            print(f"⚠️  SKIPPED: Document {doc_id} is unavailable")
            extracted_texts[doc_id] = {"status": "unavailable", 
                                       "doc_date": doc_date,
                                       "text": "", 
                                       "error": "Document unavailable"}
            continue
        
        # Check if file exists
        if not local_path.exists():
            print(f"❌ ERROR: File not found at {local_path}")
            extracted_texts[doc_id] = {"status": "error",
                                       "doc_date": doc_date,
                                       "text": "", 
                                       "error": "File not found"}
            continue
        
        # Check if it's a PDF file
        if not file_name.endswith('.pdf'):
            print(f"⚠️  SKIPPED: {file_name} is not a PDF file")
            extracted_texts[doc_id] = {"status": "skipped",
                                       "doc_date": doc_date,
                                       "text": "", 
                                       "error": "Not a PDF file"}
            continue
        
        try:
            # Extract text from PDF
            print(f"📄 Extracting text from {file_name}...")
            
            with open(local_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                raw_text_content = ""
                
                print(f"   Number of pages: {len(pdf_reader.pages)}")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        raw_text_content += f"\n--- Page {page_num} ---\n{page_text}\n"
                        print(f"   ✓ Extracted text from page {page_num}")
                    except Exception as page_error:
                        print(f"   ❌ Error extracting from page {page_num}: {page_error}")
                        continue
                
                if raw_text_content.strip():
                    # Clean the extracted text
                    print(f"🧹 Cleaning extracted text...")
                    cleaned_text = clean_extracted_text(raw_text_content)
                    
                    if cleaned_text:
                        extracted_texts[doc_id] = {
                            "status": "success", 
                            "doc_date": doc_date,
                            "text": cleaned_text, 
                            "error": None,
                            "page_count": len(pdf_reader.pages),
                            "char_count": len(cleaned_text)
                        }
                        print(f"✅ Successfully extracted and cleaned text from {doc_id}")
                        
                        print("─" * 50)
                        print(f"Character count: {len(cleaned_text)}")
                        print(f"Word count (approx): {len(cleaned_text.split())}")
                        
                    else:
                        print(f"⚠️  WARNING: No readable content after cleaning from {doc_id}")
                        extracted_texts[doc_id] = {"status": "empty", "text": "", "error": "No readable content after cleaning"}
                        
                else:
                    print(f"⚠️  WARNING: No text content extracted from {doc_id}")
                    extracted_texts[doc_id] = {"status": "empty", "text": "", "error": "No text content found"}
        
        except Exception as e:
            print(f"❌ ERROR processing {doc_id}: {str(e)}")
            extracted_texts[doc_id] = {"status": "error", "text": "", "error": str(e)}
    
    # Summary
    print(f"\n{'=' * 80}")
    print("EXTRACTION SUMMARY")
    print(f"{'=' * 80}")
    total_docs = len(upload_metadata)
    successful_extractions = len([doc for doc in extracted_texts.values() if doc["status"] == "success"])
    
    print(f"Total documents processed: {total_docs}")
    print(f"Successful extractions: {successful_extractions}")
    print(f"Failed/Skipped: {total_docs - successful_extractions}")
    
    # Show status breakdown
    status_count = {}
    for doc_id, doc_data in extracted_texts.items():
        status = doc_data["status"]
        status_count[status] = status_count.get(status, 0) + 1
        if status != "success":
            print(f"  - {doc_id}: {status} - {doc_data['error']}")
    
    print(f"\nStatus breakdown: {status_count}")
    
    return extracted_texts


def prepare_for_llm_processing(extracted_texts: Dict[str, Dict]) -> Dict[str, str]:
    """
    Prepare extracted texts specifically for LLM processing by returning only successful extractions.
    
    Args:
        extracted_texts: Dictionary from extract_text_from_pdf function
        
    Returns:
        Dictionary with doc_id as key and clean text ready for LLM as value
    """
    llm_ready_texts = {}
    
    print(f"\n{'=' * 80}")
    print("PREPARING TEXTS FOR LLM PROCESSING")
    print(f"{'=' * 80}")
    
    
    for doc_id, doc_data in extracted_texts.items():
        if doc_data["status"] == "success" and doc_data["text"]:
            llm_ready_texts[doc_id] = {
                "text": doc_data["text"],
                "doc_date": doc_data["doc_date"]
                }
            print(f"✅ {doc_id}: Ready for LLM ({doc_data['char_count']} chars, {len(doc_data['text'].split())} words) Doc Date: {doc_data['doc_date']}")
        else:
            print(f"⚠️  {doc_id}: Skipped - {doc_data['status']} ({doc_data.get('error', 'Unknown error')}) Doc Date: {doc_data['doc_date']}")
    
    print(f"\nTotal documents ready for LLM processing: {len(llm_ready_texts)}")
    
    return llm_ready_texts
