from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import RoleChecker, get_current_user
from src.db.main import get_session
from src.db.models import User
from .schemas import ReviewCreateModel
from .service import ReviewService

review_service = ReviewService()

MyAsyncSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))

review_router = APIRouter()

@review_router.post('/book/{book_uid}')
async def add_review_to_books(book_uid : str, review_data : ReviewCreateModel,
                              user : CurrentUser , session : MyAsyncSession):
    new_review = await review_service.add_review_to_book(user.email,review_data,book_uid,session)
    return new_review