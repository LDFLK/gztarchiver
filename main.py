import asyncio
import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from twisted.internet import asyncioreactor
asyncioreactor.install()
from doc_scraper.cmd import parse_args, identify_input_kind
from pathlib import Path
import yaml
from twisted.internet import reactor
from doc_scraper.crawler import run_crawlers_sequentially
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
    project_root = Path(__file__).parent   
    
    # Get config file location
    config_path = args.config

    # Load config.yaml
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Run crawlers sequentially
    run_crawlers_sequentially(args, config, project_root, user_input_kind)
    reactor.run()


if __name__ == "__main__":
    main()