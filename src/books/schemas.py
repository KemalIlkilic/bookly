from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

class Book(BaseModel):
    uid : uuid.UUID
    title: str
    author : str
    publisher : str
    published_date : str
    page_count : int
    language: str
    created_at : datetime
    updated_at : datetime

class BookCreateModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None 
    published_date : Optional[str] = None


class BookUpdateModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None