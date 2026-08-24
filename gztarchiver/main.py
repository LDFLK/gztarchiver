import asyncio
import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from twisted.internet import asyncioreactor
asyncioreactor.install()
from .doc_scraper.cmd import parse_args, identify_input_kind
from pathlib import Path
import yaml
from twisted.internet import reactor, defer
from .doc_scraper.crawler import get_crawler_pipeline, DEFAULT_VERSION
from pyfiglet import figlet_format
from termcolor import colored
    
def main():
    
    ascii_art = figlet_format('gztarchiver', font='big')
    colored_art = colored(ascii_art, color='cyan')
    print("\n" + colored_art)
    
    args = parse_args()
    user_input_kind = identify_input_kind(args)

    if user_input_kind == "invalid-input":
        print("Invalid input! --year and --lang are required at minimum.")
        sys.exit(1)
        
    if user_input_kind == "invalid-lang-input":
        print("Please enter supported language")
        print("Supported languages: en (English), si (Sinhala), ta (Tamil)")
        sys.exit(1)

    # Project root
    # project_root = Path(__file__).parent   
    
    # Get config file location
    config_path = args.config

    # Load config.yaml
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Resolve crawler version (CLI flag takes precedence, defaults to v2)
    crawler_version = (args.crawler_version or DEFAULT_VERSION).lower()
    print(f"🚀 Using Crawler Version: {crawler_version.upper()}")

    # Retrieve and execute selected pipeline
    try:
        pipeline = get_crawler_pipeline(crawler_version)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    def _execute():
        d = defer.maybeDeferred(pipeline, args, config, user_input_kind)
        def _cleanup(_):
            if reactor.running:
                reactor.stop()
        d.addBoth(_cleanup)

    reactor.callWhenRunning(_execute)
    reactor.run()




if __name__ == "__main__":
    main()