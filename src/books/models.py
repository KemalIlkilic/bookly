from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import date, datetime
import uuid


#Column is an SQLAlchemy component used to provide detailed information about database columns

class Book(SQLModel, table=True):
    #The Book model will be in a table automatically named "book"
    #now we changed to name books
    __tablename__ = "books"
    uid : uuid.UUID = Field(
        sa_column= Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    title: str
    author : str
    publisher : str
    published_date : date
    page_count : int
    language: str
    created_at : datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now))
    updated_at : datetime = Field(sa_column= Column(pg.TIMESTAMP, default=datetime.now))

    #repr(object): Return a string containing a printable representation of an object.
    def __repr__(self):
        return f"<Book {self.title}"
    


    """
    #The quotes around "Book" in List["Book"] are for forward references, allowing you to reference a class before it's defined. (line-43)
    class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    #The books field doesn't create a column in the Author table
    #Instead, it sets up a relationship that SQLModel uses to query related Book objects.
    books: List["Book"] = Relationship(back_populates="author")

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author_id: Optional[int] = Field(default=None, foreign_key="author.id")
    author: Optional[Author] = Relationship(back_populates="books")


    

#there is no column for books in author table but you can get these books with author.books
# Query example
with Session(engine) as session:
    statement = select(Author).where(Author.name == "George Orwell")
    author = session.exec(statement).first()
    print(f"Author: {author.name}")
    for book in author.books:
        print(f"- {book.title}")
    """
