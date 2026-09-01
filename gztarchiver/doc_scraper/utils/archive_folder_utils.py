from pathlib import Path
import json
from gztarchiver.models.v2.gazette import GazetteEntry

def build_download_metadata_v2(
    entries: list[GazetteEntry],
    archive_location: Path,
    archive_languages: list[str],
    cdn_proxy_url: str,
) -> list[dict]:
    """
    Convert a list of filtered GazetteEntry objects into download_metadata dicts
    compatible with PDFDownloaderSpider and post_crawl_processing.

    Args:
        entries: Filtered GazetteEntry objects to archive.
        archive_location: Root archive directory (Path).
        archive_languages: Languages to download, e.g. ["ENGLISH"].
                           Content entries whose language is not in this list
                           are skipped.
        cdn_proxy_url: Base URL for downloading gazette PDFs via content proxy.

    Returns:
        List of download_metadata dicts expected by PDFDownloaderSpider.
    """
    all_download_metadata = []

    for entry in entries:
        doc_id = entry.gazetteNoText.replace("/", "-")
        date_str = entry.date.strftime("%Y-%m-%d")
        year, month, day = date_str.split("-")

        description = (
            entry.descriptionEnglish
            or entry.descriptionSinhala
            or entry.descriptionTamil
            or doc_id
        )

        for content in entry.contents:
            if content.language not in archive_languages:
                continue

            lang_suffix = content.language.lower()
            download_url = f"{cdn_proxy_url}{content.uploadedFile}"

            file_name = f"{doc_id}_{lang_suffix}.pdf"
            folder_path = archive_location / year / month / day / doc_id
            folder_path.mkdir(parents=True, exist_ok=True)
            file_path = folder_path / file_name

            all_download_metadata.append({
                "doc_id": doc_id,
                "date": date_str,
                "des": description,
                "download_url": download_url,
                "file_name": file_name,
                "file_path": file_path,
                "availability": "Available",
            })

    return all_download_metadata


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
        
        if availability != "Available" or url == "N/A":
            print(f"📄 Unavailable document found: {doc_id} on {date_str}")
            continue
    
    return all_download_metadata

