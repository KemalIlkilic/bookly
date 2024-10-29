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

@review_router.get("/", dependencies=[admin_role_checker])
async def get_all_reviews(session: MyAsyncSession):
    books = await review_service.get_all_reviews(session)

    return books


@review_router.get("/{review_uid}", dependencies=[user_role_checker])
async def get_review(review_uid: str, session: MyAsyncSession):
    book = await review_service.get_review(review_uid, session)

    if not book:
        raise

@review_router.post('/book/{book_uid}', dependencies=[user_role_checker])
async def add_review_to_books(book_uid : str, review_data : ReviewCreateModel,
                              user : CurrentUser , session : MyAsyncSession):
    new_review = await review_service.add_review_to_book(user.email,review_data,book_uid,session)
    return new_review


@review_router.delete(
    "/{review_uid}",
    dependencies=[user_role_checker],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    review_uid: str,
    current_user: CurrentUser,
    session: MyAsyncSession,
):
    await review_service.delete_review_to_from_book(
        review_uid=review_uid, user_email=current_user.email, session=session
    )

    return None