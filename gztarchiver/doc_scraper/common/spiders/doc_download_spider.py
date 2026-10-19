import scrapy
from pathlib import Path
import csv
import json

class PDFDownloaderSpider(scrapy.Spider):
    name = "pdf_downloader"
    
    custom_settings = {
        "DOWNLOAD_DELAY": 1.0,
        "CONCURRENT_REQUESTS": 2,
        "RETRY_ENABLED": True,
        "LOG_LEVEL": "ERROR"
    }

    def __init__(self, download_metadata=None, output_path=None, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.download_metadata = download_metadata or []
        self.config = config or {}
        self.output_path = output_path
        self.archived_doc_ids = set()
        self.failed_doc_ids = set()
        self.unavailable_doc_ids = set()
    
    def check_available_data(self):
        """
        Check archived and failed log files to determine what needs to be downloaded.
        Returns filtered metadata with items that need to be processed.
        """
        # Collect unique years to check respective log files
        years = set()
        for item in self.download_metadata:
            try:
                years.add(item["file_path"].parts[-5])  # Extract year from the path
            except (IndexError, AttributeError):
                self.logger.warning(f"Could not extract year from path: {item.get('file_path', 'unknown')}")
                print(f"Could not extract year from path: {item.get('file_path', 'unknown')}")

        # Check each year's log files
        archive_root = Path(self.config["archive"]["archive_location"])
        for year in years:
            # Get base log directory for this year
            base_log_dir = archive_root / year / self.config["output"]["log_record_dir"]
            # Check archived logs
            successfully_archived_log_file = base_log_dir / self.config["output"]["log_success"]
            if successfully_archived_log_file.exists():
                self.archived_doc_ids.update(self._read_log_file(successfully_archived_log_file))
                self.logger.info(f"📋 Found {len(self.archived_doc_ids)} archived documents for {year}")
                print(f"📋 Found {len(self.archived_doc_ids)} archived documents for {year}")
            # Check failed logs
            failed_log_file = base_log_dir / self.config["output"]["log_failure"]
            if failed_log_file.exists():
                self.failed_doc_ids.update(self._read_log_file(failed_log_file))
                self.logger.info(f"🔄 Found {len(self.failed_doc_ids)} failed documents for {year}")
                print(f"🔄 Found {len(self.failed_doc_ids)} failed documents for {year}")
            # Check unavailable logs
            unavailable_log_file = base_log_dir / self.config["output"]["log_unavailable"]
            if unavailable_log_file.exists():
                self.unavailable_doc_ids.update(self._read_log_file(unavailable_log_file))
                self.logger.info(f"⚠️ Found {len(self.unavailable_doc_ids)} unavailable documents for {year}")
                print(f"⚠️ Found {len(self.unavailable_doc_ids)} unavailable documents for {year}")
        
        # Filter metadata based on archived and failed logs
        filtered_metadata = []
        unavailable_items = []
        skipped_count = 0
        retry_count = 0
        
        # Store original count to check if we need to save
        original_count = len(self.download_metadata)
        
        for item in self.download_metadata:
            doc_id = item.get("doc_id")
            url = item.get("download_url")
            if doc_id in self.archived_doc_ids:
                # Skip already archived documents
                skipped_count += 1
                self.logger.debug(f"⏭️ Skipping archived document: {doc_id}")
                print(f"⏭️ Skipping archived document: {doc_id}")
            elif not url or url == "N/A":
                # Separate unavailable items (no valid URL)
                unavailable_items.append(item)
            elif doc_id in self.failed_doc_ids:
                # Retry failed documents
                retry_count += 1
                self.logger.info(f"🔄 Retrying failed document: {doc_id}")
                print(f"🔄 Retrying failed document: {doc_id}")
                filtered_metadata.append(item)
            else:
                # New document to download
                filtered_metadata.append(item)
        
        # Remove archived documents from download_metadata to avoid rerunning
        self.download_metadata = [item for item in self.download_metadata if item.get("doc_id") not in self.archived_doc_ids]
        
        # Save updated metadata
        self.save_updated_metadata()
        
        # Process unavailable items separately
        if unavailable_items:
            self.logger.info(f"⚠️ Processing {len(unavailable_items)} unavailable documents:")
            for item in unavailable_items:
                doc_id = item.get("doc_id")
                # Create folder structure
                folder_path = item["file_path"].parent
                folder_path.mkdir(parents=True, exist_ok=True)
                # Log to unavailable.csv only if not already logged
                if doc_id not in self.unavailable_doc_ids:
                    self.log_status(item, self.config["output"]["log_unavailable"])
                    self.unavailable_doc_ids.add(doc_id)
                self.logger.info(f"⚠️ Unavailable: {doc_id}")
        
        self.logger.info(f"📊 Data check summary:")
        self.logger.info(f"   - Total documents: {original_count}")
        self.logger.info(f"   - Already archived (skipped): {skipped_count}")
        self.logger.info(f"   - Unavailable (no download URL): {len(unavailable_items)}")
        self.logger.info(f"   - Failed previously (retrying): {retry_count}")
        self.logger.info(f"   - New to download: {len(filtered_metadata) - retry_count}")
        self.logger.info(f"   - Total to download: {len(filtered_metadata)}")
        
        print(f"📊 Data check summary:")
        print(f"   - Total documents: {original_count}")
        print(f"   - Already archived (skipped): {skipped_count}")
        print(f"   - Unavailable (no download URL): {len(unavailable_items)}")
        print(f"   - Failed previously (retrying): {retry_count}")
        print(f"   - New to download: {len(filtered_metadata) - retry_count}")
        print(f"   - Total to download: {len(filtered_metadata)}")
        
        return filtered_metadata
    
    def _read_log_file(self, log_file_path):
        """Read doc_ids from a log file and return as a set."""
        doc_ids = set()
        try:
            with open(log_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    doc_id = row.get('doc_id')
                    if doc_id:
                        doc_ids.add(doc_id)
        except Exception as e:
            self.logger.error(f"❌ Error reading log file {log_file_path}: {e}")
            print(f"❌ Error reading log file {log_file_path}: {e}")
        return doc_ids

    async def start(self):
        # Check available data before starting downloads
        self.logger.info("🔍 Checking available data...")
        filtered_metadata = self.check_available_data()
        for item in filtered_metadata:
            url = item.get("download_url")
            # Since we already filtered out unavailable items, all items here should have valid URLs
            yield scrapy.Request(
                url=url,
                callback=self.save_pdf,
                errback=self.handle_failure,
                meta={"item": item},
                dont_filter=True
            )
    
    def save_pdf(self, response):
        item = response.meta["item"]
        file_path = item["file_path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(file_path, "wb") as f:
                f.write(response.body)
            self.log_status(item, self.config["output"]["log_success"])
            self.logger.info(f"✅ Downloaded: {file_path}")
            print(f"  --✅ Downloaded: {file_path}")
        except Exception as e:
            self.log_status(item, self.config["output"]["log_failure"])
            self.logger.error(f"❌ Failed to save {file_path}: {e}")
            print(f"❌ Failed to save {file_path}: {e}")
    
    def handle_failure(self, failure):
        item = failure.request.meta["item"]
        self.log_status(item, self.config["output"]["log_failure"])
        self.logger.error(f"❌ Request failed: {item['download_url']}")
        print(f"  --❌ Request failed: {item['download_url']}")
        
        # Update availability to DOWNLOAD_FAILED for failed downloads (e.g., 404 or corrupt links)
        item["availability"] = "DOWNLOAD_FAILED"

    def closed(self, reason):
        """Called by Scrapy when spider completes all requests. Saves final metadata once."""
        self.save_updated_metadata()

    def save_updated_metadata(self):
        """Save updated download_metadata to a JSON file."""
        if not self.output_path:
            self.logger.warning("No output_path specified, skipping metadata save")
            return
            
        try:            
            serializable_metadata = []
            
            for metadata_item in self.download_metadata:
                if hasattr(metadata_item, "model_dump"):
                    item_dict = metadata_item.model_dump(mode="json")
                else:
                    item_dict = dict(metadata_item)
                    if "file_path" in item_dict:
                        item_dict["file_path"] = str(item_dict["file_path"])
                serializable_metadata.append(item_dict)
                
            output_file = Path(self.output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as jsonfile:
                json.dump(serializable_metadata, jsonfile, indent=4)
            self.logger.info(f"📝 Updated metadata saved to: {self.output_path}")
            print(f"    📝 Updated metadata saved to: {self.output_path}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save updated metadata: {e}")
            print(f"❌ Failed to save updated metadata: {e}")
    
    def _upsert_csv_row(self, log_file: Path, doc_id: str, row_data: list):
        """Insert or update a row in a CSV log file by doc_id without duplicates."""
        rows = {}
        header = ["doc_id", "download_url", "file_path"]
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    file_header = next(reader, None)
                    if file_header:
                        header = file_header
                    for r in reader:
                        if r and len(r) > 0:
                            rows[r[0]] = r
            except Exception as e:
                self.logger.warning(f"Error reading {log_file} for upsert: {e}")

        rows[doc_id] = row_data

        with open(log_file, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for r in rows.values():
                writer.writerow(r)

    def _remove_csv_row(self, log_file: Path, doc_id: str):
        """Remove a row with doc_id from a CSV log file if present."""
        if not log_file.exists():
            return
        try:
            rows = []
            header = ["doc_id", "download_url", "file_path"]
            found = False
            with open(log_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                file_header = next(reader, None)
                if file_header:
                    header = file_header
                for r in reader:
                    if r and len(r) > 0 and r[0] == doc_id:
                        found = True
                    elif r:
                        rows.append(r)

            if found:
                with open(log_file, "w", newline='', encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
                    for r in rows:
                        writer.writerow(r)
        except Exception as e:
            self.logger.warning(f"Error removing {doc_id} from {log_file}: {e}")

    def log_status(self, item, status):
        try:
            year = item["file_path"].parts[-5]  # Extract year from the path
            base_log_dir = Path(item["file_path"]).parents[4] / year / self.config["output"]["log_record_dir"]
            base_log_dir.mkdir(parents=True, exist_ok=True)
            log_file = base_log_dir / f"{status}"

            if status == self.config["output"]["log_unavailable"]:
                file_location = item["file_path"].parent
            else:
                file_location = item["file_path"]

            row_data = [item["doc_id"], item["download_url"], str(file_location)]
            self._upsert_csv_row(log_file, item["doc_id"], row_data)

            # If document was successfully archived, clean it from failed and unavailable logs
            if status == self.config["output"].get("log_success"):
                failed_log = base_log_dir / self.config["output"]["log_failure"]
                unavailable_log = base_log_dir / self.config["output"]["log_unavailable"]
                self._remove_csv_row(failed_log, item["doc_id"])
                self._remove_csv_row(unavailable_log, item["doc_id"])

        except Exception as e:
            self.logger.error(f"❌ Failed to log status for {item.get('doc_id', 'unknown')}: {e}")
            print(f"❌ Failed to log status for {item.get('doc_id', 'unknown')}: {e}")
