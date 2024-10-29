from pydantic import BaseModel
from typing import Optional, List
from src.reviews.schemas import ReviewModel
import uuid
from datetime import datetime, date

class Book(BaseModel):
    uid : uuid.UUID
    title: str
    author : str
    publisher : str
    published_date : date
    page_count : int
    language: str
    created_at : datetime
    update_at : datetime

class BookDetailModel(Book):
    reviews: List[ReviewModel]

class BookCreateModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None 
    published_date : Optional[date] = None


class BookUpdateModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None