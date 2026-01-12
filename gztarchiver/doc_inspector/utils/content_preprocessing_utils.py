import PyPDF2
import re
from pathlib import Path
from typing import List, Dict, Any
import unicodedata
import fitz 

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

def extract_text_from_pdf(all_download_metadata: List[Dict[str, Any]], chunk_size: int = 20) -> Dict[str, str]:
    """
    Extract and clean text from PDF documents in chunks to avoid freezing on large files.
    Uses PyMuPDF for faster and more reliable extraction.
    Modified to only read the first 3 pages of each document.
    """
    extracted_texts = {}

    print(f"{'=' * 80}")
    print("STARTING TEXT EXTRACTING PROCESS")
    print(f"{'=' * 80}")
    for doc_info in all_download_metadata:
        doc_id = doc_info['doc_id']
        doc_date = doc_info['date']
        file_name = doc_info['file_name']
        availability = doc_info['availability']
        local_path = Path(doc_info['file_path'])
        download_url = doc_info["download_url"]
        description = doc_info["des"]
        
        if availability == 'Unavailable' or file_name == 'unavailable.json':
            # extracted_texts[doc_id] = {
            #     "status": "unavailable",
            #     "date": doc_date,
            #     "text": "",
            #     "error": "Document unavailable"
            # }
            continue

        print(f"\n")
        print(f"  - Processing Document ID: {doc_id}")
        print(f"  - Document Date: {doc_date}")
        print(f"  - File Name: {file_name}")
        print(f"  - Availability: {availability}")
        print(f"  - Local Path: {local_path}")

        if not local_path.exists():
            print(f"  - ❌ ERROR: File not found at {local_path}")
            print("\n")
            extracted_texts[doc_id] = {
                "status": "error",
                "date": doc_date,
                "text": "",
                "error": "File not found",
                "file_path": local_path,
                "availability": availability,
                "download_url": download_url,
                "des": description
            }
            continue

        if not file_name.endswith('.pdf'):
            print(f"  - ⚠️  SKIPPED: {file_name} is not a PDF file")
            print("\n")
            extracted_texts[doc_id] = {
                "status": "skipped",
                "date": doc_date,
                "text": "",
                "error": "Not a PDF file",
                "file_path": local_path,
                "availability": availability,
                "download_url": download_url,
                "des": description
            }
            continue

        try:
            print(f"  - Extracting text from {file_name}...")

            doc = fitz.open(local_path)
            total_pages = len(doc)
            # Limit to first 3 pages or total pages if less than 3
            pages_to_extract = min(3, total_pages)
            
            print(f"  - Total pages in document: {total_pages}")
            print(f"  - Pages to extract: {pages_to_extract} (first {pages_to_extract} page{'s' if pages_to_extract != 1 else ''})")

            raw_text_content = ""
            for start in range(0, pages_to_extract, chunk_size):
                end = min(start + chunk_size, pages_to_extract)
                print(f"  - Processing pages {start+1}–{end}...")

                for page_num in range(start, end):
                    try:
                        page_text = doc[page_num].get_text("text")
                        raw_text_content += f"\n--- Page {page_num+1} ---\n{page_text}\n"
                        print(f"    ✓ Extracted text from page {page_num+1}")
                    except Exception as page_error:
                        print(f"    ❌ Error extracting page {page_num+1}: {page_error}")
                        continue

            doc.close()

            if raw_text_content.strip():
                print(f"  - Cleaning extracted text...")
                cleaned_text = clean_extracted_text(raw_text_content)

                if cleaned_text:
                    extracted_texts[doc_id] = {
                        "status": "success",
                        "date": doc_date,
                        "text": cleaned_text,
                        "error": None,
                        "total_page_count": total_pages,
                        "extracted_page_count": pages_to_extract,
                        "char_count": len(cleaned_text),
                        "file_path": local_path,
                        "availability": availability,
                        "download_url": download_url,
                        "des": description
                    }
                    
                    print(f"  - Character count: {len(cleaned_text)}")
                    print(f"  - Word count (approx): {len(cleaned_text.split())}")
                    print(f"  - ✅ Successfully extracted and cleaned text from {doc_id}")
                    print("\n")
                else:
                    print(f"  - ⚠️  WARNING: No readable content after cleaning from {doc_id}")
                    print("\n")
                    extracted_texts[doc_id] = {
                        "status": "empty",
                        "date": doc_date,
                        "text": "",
                        "error": "No readable content after cleaning",
                        "total_page_count": total_pages,
                        "extracted_page_count": pages_to_extract,
                        "file_path": local_path,
                        "availability": availability,
                        "download_url": download_url,
                        "des": description
                    }

            else:
                print(f"  - ⚠️  WARNING: No text content extracted from {doc_id}")
                print("\n")
                extracted_texts[doc_id] = {
                    "status": "empty",
                    "date": doc_date,
                    "text": "",
                    "error": "No text content found",
                    "total_page_count": total_pages,
                    "extracted_page_count": pages_to_extract,
                    "file_path": local_path,
                    "availability": availability,
                    "download_url": download_url,
                    "des": description
                }

        except Exception as e:
            print(f"  - ❌ ERROR processing {doc_id}: {str(e)}")
            print("\n")
            extracted_texts[doc_id] = {
                "status": "error",
                "date": doc_date,
                "text": "",
                "error": str(e),
                "file_path": local_path,
                "availability": availability,
                "download_url": download_url,
                "des": description
            }

    # Summary
    print("EXTRACTION SUMMARY")
    total_docs = len([ item for item in all_download_metadata if item.get("availability") != "Unavailable"])
    successful_extractions = len([doc for doc in extracted_texts.values() if doc["status"] == "success"])

    print(f"Total documents processed: {total_docs}")
    print(f"Successful extractions: {successful_extractions}")
    print(f"Failed/Skipped: {total_docs - successful_extractions}")

    status_count = {}
    for doc_id, doc_data in extracted_texts.items():
        status = doc_data["status"]
        status_count[status] = status_count.get(status, 0) + 1
        if status != "success":
            print(f"  - {doc_id}: {status} - {doc_data['error']}")

    if not status_count:
        print("Status breakdown: 0 documents processed")
    else:
        print(f"Status breakdown: {status_count}")
    
    print(f"{'-' * 80}")

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
    print("PREPARING TEXT FOR LLM PROCESSING")
    print(f"{'=' * 80}")
    
    for doc_id, doc_data in extracted_texts.items():
        if doc_data["status"] == "success" and doc_data["text"]:
            llm_ready_texts[doc_id] = {
                "text": doc_data["text"],
                "date": doc_data["date"],
                "file_path": doc_data["file_path"],
                "availability": doc_data["availability"],
                "download_url": doc_data["download_url"],
                "des": doc_data["des"]
                }
            print(f" - {doc_id}: Ready    ✅")
        else:
            print(f" - {doc_id}: Skipped  ⏭️")
    
    print(f"Total documents ready for LLM processing: {len(llm_ready_texts)}\n")
    
    return llm_ready_texts