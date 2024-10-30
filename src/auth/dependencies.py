from typing import Annotated, Any, List
from fastapi.security import HTTPBearer
from fastapi import Request , status, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from fastapi.exceptions import HTTPException
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import UserService
from src.db.models import User
from src.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
    AccountNotVerified
    )


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)

    """
    The __call__ method runs whenever an instance of the class is used as a function.
    In your FastAPI application, this happens when the token bearer is used as a dependency.

    #1. First we create an instance of TokenBearer (or its subclasses)
    access_token_bearer = AccessTokenBearer()
    #2. Then we use it as a dependency in a route
    @router.get("/protected")
    async def protected_route(token_data: Annotated[dict, Depends(access_token_bearer)]):
        return {"message": "Protected data"}

    When this route is accessed, FastAPI will:

    1)See that there's a dependency Depends(access_token_bearer)
    2)Call the access_token_bearer instance as if it were a function
    3)This triggers the __call__ method
    """
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        #token : eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImVtYWlsIjoia2VtYWxAZG1jYS5pbyIsInVzZXJfdWlkIjoiMmWExLWJhZWItNmI2MWNkMjgxNDYxIn0sImV4cCI6MTcyOTQ2ODU5NiwianRpIjoiPGZ1bmN0aW9uIHV1aWQ0IGF0IDB4MTAwZjVjYzIwPiIsInJlZnJlc2giOmZhbHNlfQ.ChXWrUpxC7rvyAwvGBHx-jh3-HQ289TGiXV7JXN353A
        token = creds.credentials

        if not self.token_valid(token):
            raise InvalidToken()
        
        
        #token_data : {'user': {'email': 'kemal@dmca.io', 'user_uid': '2e53a3'},
        #              'exp': 1729468596, 'jti': '<function uuid4 at 0x100f5cc20>', 'refresh': False}
        token_data = decode_token(token)
        if not token_data:
            raise InvalidToken()
        
        if await token_in_blocklist(token_data['jti']):
            raise InvalidToken()
        """
        When the __call__ method runs, it calls self.verify_token_data(token_data).
        The interesting part is that self will refer to either an AccessTokenBearer or RefreshTokenBearer instance, not the base TokenBearer.
        This is polymorphism in action!
        Request with token -> TokenBearer.__call__() -> self.verify_token_data() => 
        1) for AccessTokenBearer => verify_token_data() , it will checks    (checks refresh=False)
        2) for RefreshTokenBearer => verify_token_data() , it will checks    (checks refresh=True)
        """
        
        self.verify_token_data(token_data)

        return token_data
    
    def token_valid(self, token : str) -> bool :
        return True if decode_token(token) else False
    
    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")
    

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self,token_data : dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()
        #It means that it is not access token , actually it is refresh token

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()

access_token_bearer = AccessTokenBearer()
AccessTokenDetails = Annotated[dict,Depends(access_token_bearer)]
MyAsyncSession = Annotated[AsyncSession, Depends(get_session)]
user_service = UserService()
async def get_current_user(token_details : AccessTokenDetails ,session : MyAsyncSession):
    user_email = token_details["user"]["email"]
    user = await user_service.get_user_by_email(user_email, session)
    return user


"""
# Creating instances
access_checker = AccessTokenBearer()
refresh_checker = RefreshTokenBearer()

# Same token data, different behaviors
token_data = {
    "refresh": False,  # This is an access token
    "user": {"email": "user@example.com"}
}

# This will succeed (access token checker with access token)
access_checker.verify_token_data(token_data)  

# This will raise an exception (refresh token checker with access token)
refresh_checker.verify_token_data(token_data)  # Raises HTTPException

# If we change refresh to True
token_data["refresh"] = True

# Now the opposite happens:
access_checker.verify_token_data(token_data)   # Raises HTTPException
refresh_checker.verify_token_data(token_data)  # Succeeds
"""



class RoleChecker:
    def __init__(self, allowed_roles : List[str]) -> None:
        self.allowed_roles =  allowed_roles

    def __call__(self, current_user : Annotated[User,Depends(get_current_user)]) -> Any:
        if not current_user.is_verified:
            raise AccountNotVerified()
        if current_user.role in self.allowed_roles:
            return True
        raise InsufficientPermission()