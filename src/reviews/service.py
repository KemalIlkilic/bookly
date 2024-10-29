from fastapi.exceptions import HTTPException
from fastapi import status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from datetime import datetime
from src.reviews.schemas import ReviewCreateModel

book_service = BookService()
user_service = UserService()

class ReviewService:
    async def add_review_to_book(self, user_email : str, review_data : ReviewCreateModel , book_uid : str, session : AsyncSession):
        try:
            book = await book_service.get_book(book_uid,session)
            if not book:
                raise HTTPException(
                    detail="Book not found", status_code=status.HTTP_404_NOT_FOUND
                )
            user = await user_service.get_user_by_email(user_email,session)
            if not user:
                raise HTTPException(
                    detail="User not found", status_code=status.HTTP_404_NOT_FOUND
                )
            review_data_dict = review_data.model_dump()

            new_review = Review(**review_data_dict)
            new_review.user = user
            new_review.book = book

            session.add(new_review)
            await session.commit()
            return new_review
        
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ooops... Something went wrong")