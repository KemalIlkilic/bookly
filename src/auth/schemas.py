from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from typing import List
from src.books.schemas import Book

class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username : str = Field(max_length=10)
    email : str = Field(max_length=50)
    password : str = Field(min_length=4)

class UserModel(BaseModel):
    uid : uuid.UUID
    username : str
    email : str
    first_name : str
    last_name : str
    is_verified : bool
    #The original password is never stored
    password_hash : str = Field(exclude=True)
    created_at: datetime
    update_at: datetime


class UserBooksModel(UserModel):
    books: List[Book]

class UserLoginModel(BaseModel):
        email : str = Field(max_length=50)
        password : str = Field(min_length=4)