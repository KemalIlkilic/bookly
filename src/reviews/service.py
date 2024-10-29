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

            #SQLModel will automatically set the user_uid and book_uid fields based on the user and book objects you provide.
            #Relationships between the User and Book objects need to be properly set up in the database 
            #For the automatic assignment of user_uid and book_uid in the Review model to work.
            new_review = Review(**review_data_dict, user=user, book = book)

            session.add(new_review)
            await session.commit()
            return new_review
        
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ooops... Something went wrong")
        

    async def get_review(self, review_uid: str, session: AsyncSession):
        statement = select(Review).where(Review.uid == review_uid)

        result = await session.exec(statement)

        return result.first()
    
    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))

        result = await session.exec(statement)

        return result.all()
    

    async def delete_review_to_from_book(
        self, review_uid: str, user_email: str, session: AsyncSession
    ):
        user = await user_service.get_user_by_email(user_email, session)

        review = await self.get_review(review_uid, session)

        if not review or (review.user != user):
            raise HTTPException(
                detail="Cannot delete this review",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        session.delete(review)

        await session.commit()