from fastapi.security import HTTPBearer
from fastapi import Request , status
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from fastapi.exceptions import HTTPException

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        #token : eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImVtYWlsIjoia2VtYWxAZG1jYS5pbyIsInVzZXJfdWlkIjoiMmU1M2EzNTItYzI1Zi00OWExLWJhZWItNmI2MWNkMjgxNDYxIn0sImV4cCI6MTcyOTQ2ODU5NiwianRpIjoiPGZ1bmN0aW9uIHV1aWQ0IGF0IDB4MTAwZjVjYzIwPiIsInJlZnJlc2giOmZhbHNlfQ.ChXWrUpxC7rvyAwvGBHx-jh3-HQ289TGiXV7JXN353A
        token = creds.credentials

        if not self.token_valid(token):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired token")
        
        #token_data : {'user': {'email': 'kemal@dmca.io', 'user_uid': '2e53a352-c25f-49a1-baeb-6b61cd281461'},
        #              'exp': 1729468596, 'jti': '<function uuid4 at 0x100f5cc20>', 'refresh': False}
        token_data = decode_token(token)
        if not token_data:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="There is no data in token_data")
        
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
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please provide an access token")
        #It means that it is not access token , actually it is refresh token

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please provide an refresh token")









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