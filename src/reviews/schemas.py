from pydantic import BaseModel, Field
import uuid
from datetime import datetime, date
from typing import Optional

class ReviewModel(BaseModel):
    uid : uuid.UUID
    rating: int = Field(lt=5)
    review_text : str
    #user_uid : Optional[uuid.UUID]
    user_uid: uuid.UUID | None
    book_uid: uuid.UUID | None
    created_at : datetime
    update_at : datetime

class ReviewCreateModel(BaseModel):
    rating : int
    review_text : str