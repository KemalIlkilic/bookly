from fastapi import APIRouter , status , Depends

from ..mail import create_message, mail
from .schemas import UserCreateModel, UserModel, UserLoginModel, UserBooksModel, EmailModel
from .service import UserService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from typing import Annotated
from fastapi.exceptions import  HTTPException
from .utils import create_access_token, decode_token, verify_password
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.db.redis import add_jti_to_blocklist
from src.errors import UserAlreadyExists, UserNotFound, InvalidCredentials, InvalidToken


user_service = UserService()
auth_router = APIRouter()
refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()


MyAsyncSession = Annotated[AsyncSession, Depends(get_session)]
RefreshTokenDetails = Annotated[dict,Depends(refresh_token_bearer)]
AccessTokenDetails = Annotated[dict,Depends(access_token_bearer)]

# Instance creation - __init__ runs immediately
AdminOnly = Annotated[bool, Depends(RoleChecker(["admin"]))]
UserAndAdmin = Annotated[bool, Depends(RoleChecker(["admin", "user"]))]


REFRESH_TOKEN_EXPIRY=7



@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses

    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to our app"

    message = create_message(recipients=emails, subject=subject, body=html)
    await mail.send_message(message)

    return {"message": "Email sent successfully"}

@auth_router.post('/signup' , response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data : UserCreateModel , session : MyAsyncSession ):
    email = user_data.email
    is_exist = await user_service.user_exists_by_email(email , session)
    if is_exist:
        # This:
        raise UserAlreadyExists()
        # Gets caught by FastAPI, which then:
        # 1. Sees it's a UserAlreadyExists exception
        # 2. Looks up the registered handler
        # 3. Returns the pre-defined response:
    new_user = await user_service.create_user(user_data, session)
    return new_user

@auth_router.post('/login')
async def login_users(login_data: UserLoginModel, session : MyAsyncSession):
    email = login_data.email
    password = login_data.password
    is_exist = await user_service.user_exists_by_email(email, session)
    if is_exist:
        user = await user_service.get_user_by_email(email,session)
        hashed_password_in_database = user.password_hash
        is_password_true = verify_password(password, hashed_password_in_database )
        if is_password_true:
            access_token = create_access_token(
                user_data= {'email' : user.email, 'user_uid' : str(user.uid), "role" : user.role}
            )
            refresh_token = create_access_token(
                user_data= {'email' : user.email, 'user_uid' : str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )
            return JSONResponse(
                content={
                    "message":"Login succesfull",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email":user.email,
                        "uid":str(user.uid)
                    }
                }
            )
    raise InvalidCredentials()


@auth_router.get('/refresh_token')
async def get_new_access_token(token_details : RefreshTokenDetails):
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})
    raise InvalidToken()

@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(authorized : UserAndAdmin ,user = Depends(get_current_user)):
    #RoleChecker Instance's __call__ runs when this endpoint is accessed
    """__call__ executes:
    When the instance is used as a function
    When FastAPI actually needs to check the authorization
    For each request to a protected endpoint
    Not during instance creation or dependency setup
    """
    return user


@auth_router.get("/logout")
async def revooke_token(token_details : AccessTokenDetails):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK
    )