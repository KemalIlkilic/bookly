from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from typing import List, Annotated
from src.db.main import get_session
from src.books.schemas import Book, BookUpdateModel, BookCreateModel, BookDetailModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.errors import BookNotFound

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()

MyAsyncSession = Annotated[AsyncSession, Depends(get_session)]
TokenDetails = Annotated[dict,Depends(access_token_bearer)]

role_checker = RoleChecker(["admin", "user"])
authorize = Depends(role_checker)

@book_router.get("/", response_model=List[Book], dependencies=[authorize])
async def get_all_books(session : MyAsyncSession, token_details : TokenDetails):
    #token_details : {'user': {'email': 'kemal@dmca.io', 'user_uid': '2e53a352-c25f-61cd281461'},
    #            'exp': 1729468596, 'jti': '<function uuid4 at 0x100f5cc20>', 'refresh': False}
    books = await book_service.get_all_books(session)
    return books

@book_router.get("/user/{user_uid}", response_model=List[Book], dependencies=[authorize])
async def get_user_book_submissions(user_uid : str , session : MyAsyncSession, token_details : TokenDetails):
    #token_details : {'user': {'email': 'kemal@dmca.io', 'user_uid': '2e53a352-c25f-61cd281461'},
    #            'exp': 1729468596, 'jti': '<function uuid4 at 0x100f5cc20>', 'refresh': False}
    books = await book_service.get_user_books(user_uid,session)
    return books



@book_router.post("/", status_code=status.HTTP_201_CREATED , response_model=Book, dependencies=[authorize])
async def create_a_book(book_data : BookCreateModel, session : MyAsyncSession, token_details: TokenDetails): 
    user_id = token_details['user']['user_uid']
    new_book = await book_service.create_book(book_data, user_id ,session)
    return new_book


@book_router.get("/{book_uid}" , response_model=BookDetailModel, dependencies=[authorize])
async def get_book(book_uid : str, session : MyAsyncSession, token_details: TokenDetails):
    book = await book_service.get_book(book_uid, session)
    if book:
        return book
    raise BookNotFound()


@book_router.patch("/{book_uid}", response_model=Book, dependencies=[authorize])
async def update_book(book_uid : str, book_update_data : BookUpdateModel, session : MyAsyncSession, token_details: TokenDetails) :
    updated_book = await book_service.update_book(book_uid, book_update_data, session )
    if updated_book:
        return updated_book
    raise BookNotFound()


@book_router.delete("/{book_uid}", dependencies=[authorize])
async def delete_book(book_uid : str, session : MyAsyncSession, token_details: TokenDetails):
    book_to_delete = await book_service.delete_book(book_uid, session)
    if book_to_delete is None:
        raise BookNotFound()
    return {"message" : "book deleted successfully"}
    