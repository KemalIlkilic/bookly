from fastapi import APIRouter , status , Depends
from .schemas import UserCreateModel, UserModel
from .service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from typing import Annotated
from fastapi.exceptions import  HTTPException

user_service = UserService()
auth_router = APIRouter()

@auth_router.post('/signup' , response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data : UserCreateModel , session : Annotated[AsyncSession, Depends(get_session)] ):
    email = user_data.email
    is_exist = await user_service.user_exists_by_email(email , session)
    if is_exist:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with email already exists")
    new_user = await user_service.create_user(user_data, session)
    return new_user