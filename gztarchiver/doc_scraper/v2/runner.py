from __future__ import annotations

import json
import logging
import requests
from pathlib import Path

from scrapy.crawler import CrawlerRunner
from twisted.internet import defer

from gztarchiver.doc_scraper.utils import (
    build_download_metadata_v2,
    hide_logs,
    load_doc_metadata_file,
)
from gztarchiver.doc_scraper.common.post_processing import post_crawl_processing
from gztarchiver.doc_scraper.common.spiders import PDFDownloaderSpider
from gztarchiver.models import DownloadMetadata, GazetteApiResponse

logger = logging.getLogger(__name__)


@defer.inlineCallbacks
def run_v2_pipeline(args, config, user_input_kind):
    """
    V2 Crawler pipeline entrypoint.

    Steps:
      1. Resolve the Next.js `next-action` token from config.yaml.
      2. Paginate the API using server-side date filtering via the `forwarded` field.
      3. Validate the response with Pydantic.
      4. Build download metadata (folder structure + file paths).
      5. Download PDFs via PDFDownloaderSpider (skips already-archived docs).
      6. Run post-processing if classification is enabled in config.yaml.

    Args:
        args: CLI arguments (args.year, args.month, args.day, args.lang).
        config: Loaded config.yaml dictionary.
        user_input_kind: One of 'year-lang', 'year-month-lang', 'year-month-day-lang'.
    """

    # Resolve v2 specific configurations
    v2_config = config.get("v2", {})
    scrape_url = config["scrape"]["url"]
    cdn_proxy_url = v2_config.get("cdn_proxy_url", "https://documents.gov.lk/api/content-file-proxy?file=")
    api_endpoint = v2_config.get("api_endpoint", "http://gvp-api:4500/website-data/extra-gazette/get-all")
    LANG_MAP = {"en": "ENGLISH", "si": "SINHALA", "ta": "TAMIL"}

    # Resolve paths
    output_path_download = config["output"]["download_metadata_json"]
    OUTPUT_PATH_DOWNLOAD = Path(output_path_download)
    OUTPUT_PATH_DOWNLOAD.parent.mkdir(parents=True, exist_ok=True)

    archive_location = Path(config["archive"]["archive_location"])

    def _build_date_range(user_input_kind: str) -> tuple[str, str]:
        """Build dateFrom and dateTo strings for the API forwarded filter."""
        year = int(args.year)
        if user_input_kind == "year-lang":
            return f"{year}-01-01", f"{year}-12-31"
        elif user_input_kind == "year-month-lang":
            month = int(args.month)
            # last day of month via rolling to day 0 of next month
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            return f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last_day:02d}"
        else:  # year-month-day-lang
            day = int(args.day)
            month = int(args.month)
            import datetime
            try:
                datetime.date(year, month, day)
            except ValueError as e:
                raise ValueError(f"Invalid date --year {year} --month {month} --day {day}: {e}") from e
            return f"{year}-{month:02d}-{day:02d}", f"{year}-{month:02d}-{day:02d}"

    def _fetch_all_matching() -> list:
        """
        Paginate through the API using server-side date filtering.
        The API filters entries via the forwarded dateFrom/dateTo fields,
        so no client-side filtering or early-stop is needed.

        Returns:
            All matching GazetteEntry objects across all pages fetched.
        """
        headers = {
            "Accept": "text/x-component",
            "Content-Type": "text/plain;charset=UTF-8",
            "next-action": token,
        }
        date_from, date_to = _build_date_range(user_input_kind)
        page_size = 100
        collected = []
        current_page = 1

        while True:
            payload = [{
                "apiEndpoint": api_endpoint,
                "page": current_page,
                "limit": page_size,
                "q": "",
                "search": "",
                "forwarded": {
                    "dateFrom": date_from,
                    "dateTo": date_to,
                },
            }]

            response = requests.post(
                scrape_url,
                headers=headers,
                json=payload,
                timeout=(30, 90),
            )
            response.raise_for_status()

            # Next.js next-action endpoints return RSC wire format — NOT plain JSON.
            # The body is newline-delimited frames, each prefixed with `<index>:`:
            #   0:{"a":"$@1","f":"","b":"..."}  ← routing metadata
            #   1:{"data":[...], "count":...}    ← actual payload
            body = response.content.decode("utf-8")
            frames: dict = {}
            for line in body.split("\n"):
                line = line.strip()
                if not line:
                    continue
                idx, sep, json_str = line.partition(":")
                if not sep:
                    continue
                try:
                    frames[idx] = json.loads(json_str)
                except json.JSONDecodeError:
                    continue

            raw = next(
                (v for v in frames.values() if isinstance(v, dict) and "data" in v),
                None,
            )
            if raw is None:
                raise ValueError("Could not find data frame in RSC response")

            page_response = GazetteApiResponse(**raw)
            entries = page_response.data

            if not entries:
                print(f"  Page {current_page}: empty — stopping.")
                break

            collected.extend(entries)

            total_pages = page_response.pagination.totalPages
            print(f"  Page {current_page}/{total_pages}: {len(entries)} entries, {len(collected)} total so far.")

            if current_page >= total_pages:
                break

            current_page += 1

        return collected

    try:
        # Step 1 — Retrieve the Next.js server-action token from configuration
        token = v2_config.get("next_action_token")
        if not token:
            print("Error: 'next_action_token' is not configured in config.yaml under 'v2:'.")
            return None

        print(f"captured next action token {token}")

        # Step 2 — Fetch required data from the API and validate with Pydantic
        print("Fetching gazette data from API...")
        matching_entries = _fetch_all_matching()
        print(f"{len(matching_entries)} entries found matching the requested date range.")

        if not matching_entries:
            print("No documents found for the given parameters.")
            return

        # Step 3 — Build download metadata for requested language
        requested_lang = LANG_MAP.get(str(args.lang), "ENGLISH")
        all_download_metadata = build_download_metadata_v2(
            entries=matching_entries,
            archive_location=archive_location,
            archive_languages=[requested_lang],
            cdn_proxy_url=cdn_proxy_url,
        )

        if not all_download_metadata:
            print(f"No documents found for the given parameters.")
            return

        available_count = sum(1 for m in all_download_metadata if m.get("availability") == "Available")
        unavailable_count = sum(1 for m in all_download_metadata if m.get("availability") == "Unavailable")
        print(f"{available_count} documents available, {unavailable_count} unavailable for language '{requested_lang}'.")
        print(f"{len(all_download_metadata)} files queued for processing.")

        # Step 4 — Download PDFs via shared PDFDownloaderSpider
        settings = hide_logs()
        runner = CrawlerRunner(settings=settings)
        yield runner.crawl(
            PDFDownloaderSpider,
            download_metadata=all_download_metadata,
            output_path=str(output_path_download),
            config=config,
        )
        print("All downloads completed successfully.")

        # Reload from file — the spider updates availability for any failed
        # downloads before saving, so this reflects the actual final state.
        raw_download_metadata = load_doc_metadata_file(str(output_path_download))

        if raw_download_metadata is None:
            raise RuntimeError(
                f"Updated download metadata not found at {output_path_download};"
            )

        updated_download_metadata = [DownloadMetadata(**item) for item in raw_download_metadata]
        
        yield defer.maybeDeferred(
            post_crawl_processing, args, config, updated_download_metadata, str(archive_location)
        )

    except Exception as e:
        print("Error during V2 crawling: ", e)
        raise
