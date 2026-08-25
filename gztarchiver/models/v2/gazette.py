from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class GazetteContent(BaseModel):
    """A single language version of a gazette document."""
    language: str                  
    originalFileName: str
    uploadedFile: str              


class GazetteEntry(BaseModel):
    """A single gazette entry as returned by the V2 API."""
    id: str
    gazetteNo: int
    gazetteSubNo: int
    gazetteNoText: str             
    date: datetime
    descriptionSinhala: Optional[str] = None
    descriptionTamil: Optional[str] = None
    descriptionEnglish: Optional[str] = None
    keywordsSinhala: Optional[str] = None
    keywordsTamil: Optional[str] = None
    keywordsEnglish: Optional[str] = None
    updatedAt: datetime
    contents: list[GazetteContent]


class Pagination(BaseModel):
    """Pagination metadata returned alongside the data."""
    total: int
    page: int
    limit: int
    totalPages: int


class GazetteApiResponse(BaseModel):
    """Top-level V2 API response envelope."""
    data: list[GazetteEntry]
    pagination: Pagination
