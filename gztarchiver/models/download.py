from pathlib import Path
from typing import Optional, Union, Any
from pydantic import BaseModel, ConfigDict

class DownloadMetadata(BaseModel):
    """Metadata for a document queued for downloading and processing."""
    doc_id: str
    date: str
    des: Optional[str] = None
    download_url: str
    file_name: str
    file_path: Union[Path, str]
    availability: str

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)
