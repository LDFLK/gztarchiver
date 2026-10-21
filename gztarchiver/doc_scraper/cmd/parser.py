import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Gazette Document Downloader CLI")

    parser.add_argument('--year', type=int, required=True, help='Year of documents (e.g. 2025)')
    parser.add_argument('--month', type=int, choices=range(1, 13), help='Month of documents (1-12)')
    parser.add_argument('--day', type=int, choices=range(1, 32), help='Day of documents (1-31)')
    parser.add_argument('--lang', type=str, required=True, help='Language code (e.g. "en", "si", "ta")')
    parser.add_argument('--config', type=str, required=True, help='Config to the programme')
    parser.add_argument(
        '--cv',
        dest='crawler_version',
        type=str,
        choices=['v1', 'v2'],
        default=None,
        help='Crawler version to use (v1 for legacy HTML scraper, v2 for new website/API). Defaults to v2.'
    )
    
    return parser.parse_args()

