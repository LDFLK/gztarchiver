from datetime import datetime, date
import json
from typing import List, Dict, Optional

def load_years_metadata(json_path: str) -> List[Dict[str, str]]:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def get_year_link(year: str, metadata: List[Dict[str, str]]) -> Optional[str]:
    for entry in metadata:
        if entry.get("year") == str(year):
            return entry.get("link")
    return None

def dynamic_page_size_based_on_date(
    target_date: str, 
    base_size: int = 50,
    daily_rate: float = 20, 
    min_page_size: int = 50, 
    max_page_size: int = 1500
    ) -> int:
    """ 
        This function calculates and returns the page size based on the given target date. 

        Args:
            target_date: Date string ('YYYY-MM-DD')
            base_size: base buffer size
            daily_rate: Avg gazzetts publications per day
            min_page_size: Lower bound limit for API requests
            max_page_size: Upper bound limit to avoid server timeouts

        return:
            size of the page size
    """

    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date,"%Y-%m-%d").date()

    today = date.today()
    days_ago = max(0, (today - target_date).days)
    
    estimated_size = int(base_size + (days_ago * daily_rate))

    return max(min_page_size, min(estimated_size, max_page_size)) 
