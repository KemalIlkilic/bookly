#A session object is a way to manage database connections and transactions.
#It acts as an interface between your application code and the database.
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from .models import Book
from datetime import datetime

class BookService:
    #Sessions are used to interact with the database:
    async def get_all_books(self, session:AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_uid : str ,session:AsyncSession) -> dict:
        statement = select(Book).where(Book.uid == book_uid )
        result = await session.exec(statement)
        book = result.first()
        return book if book else None

    async def create_book(self, book_data : BookCreateModel, session:AsyncSession):
        book_dict = book_data.model_dump(exclude_unset=True)
        new_book = Book(**book_dict)
        if book_dict.get('published_date'):
            new_book.published_date = datetime.strptime(str(book_dict['published_date']), "%Y-%m-%d")
        
        #adding an object to the session marks it as pending, meaning it will be inserted into the database when the transaction is committed.
        #session.add() is not an asynchronous operation because It's not communicating with the database at this point
        session.add(new_book)
        #By calling commit(), SQLModel will execute the necessary SQL INSERT statement to save the new_book object to the database.
        await session.commit()
        return new_book

    async def update_book(self, book_uid : str , update_data : BookUpdateModel, session:AsyncSession):
        book_to_update = await self.get_book(book_uid,session)
        if book_to_update is None:
            return None
        if book_to_update:
            #This prevents None values or default values from overwriting existing fields in the database.
            #None olan key-value'lari siliyor. Bosuna yer kaplamiyorlar.ß
            """
            With exclude_unset == True , {"title": "New Title"}
            Without exclude_unset == True , {"title": "New Title","author": None, "published_date": None }
            """
            update_data_dict = update_data.model_dump(exclude_unset=True)
            book_to_update.sqlmodel_update(update_data_dict)
            #Adds the modified book instance to the session, Marks it for update in the database
            session.add(book_to_update)
            await session.commit()
            #Refreshes the book instance from the database, Ensures we have the most up-to-date data
            await session.refresh(book_to_update)
            return book_to_update
    

    async def delete_book(self, book_uid : str ,session:AsyncSession):
        book_to_delete = await self.get_book(book_uid,session)

        if book_to_delete is not None:
            await session.delete(book_to_delete)

            await session.commit()

            return {}

        else:
            return None