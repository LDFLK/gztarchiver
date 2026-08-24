import logging
from pathlib import Path
from scrapy.crawler import CrawlerRunner
from gztarchiver.doc_scraper.utils import hide_logs
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def run_v2_pipeline(args, config, user_input_kind):
    """
    V2 Crawler pipeline entrypoint.
    
    Args:
        args: CLI arguments (args.year, args.month, args.day, args.lang, args.config, args.crawler_version)
        config: Loaded config.yaml dictionary
        user_input_kind: Input type string (e.g. 'year-lang', 'year-month-lang', 'year-month-day-lang')
    """
    
    # Hide logs (scrapy)
    settings = hide_logs()
    
    # Initiate crawling runner
    runner = CrawlerRunner(settings=settings)
    
    # Resolve paths
    output_path = config["output"]["years_json"]
    OUTPUT_PATH = Path(output_path)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    output_path_doc_metadata = config["output"]["doc_metadata_json"]
    OUTPUT_PATH_DOC_METADATA = Path(output_path_doc_metadata)
    OUTPUT_PATH_DOC_METADATA.parent.mkdir(parents=True, exist_ok=True)

    try:

        # 1. catch the server function hash
        def intercept_next_action_token():
            """
            Opens a headless browser, clicks a document action button, and captures
            the exact value of the 'next-action' header from the outgoing POST request.
            Pagination is client-side only — the next-action POST fires on doc buttons.
            """
            captured_token = None
            

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                def handle_request(request):
                    nonlocal captured_token
                    if "next-action" in request.headers:
                        captured_token = request.headers["next-action"]
                        print('captured next action token', captured_token)

                page.on("request", handle_request)
                page.goto(config["scrape"]["url"], wait_until="networkidle")

                browser.close()

                return captured_token

        token = intercept_next_action_token()

        if not token:
            logger.error('next-action token not found')
            return None

        

    except Exception as e:
        print("Error during V2 crawling: ", e)


    
