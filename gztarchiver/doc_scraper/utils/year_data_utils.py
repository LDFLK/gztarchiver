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

