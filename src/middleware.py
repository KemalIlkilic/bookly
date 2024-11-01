#Each request made to the server will pass through the middleware before it is handled by the route handlers.
#Once the server has handled the request,
#a response is generated and still passes through the middleware before being returned to the client.

"""
Client <=> Server <=> App
Client <=> Server <=> Middleware <=> App
Server <=> ServerErrorMiddleware <=> Exception Middleware <=> Custom Middleware <=> Application


Logging: Middleware can modify how the server logs details of requests and responses for monitoring
and debugging purposes.

Authentication: Middleware can handle authentication by verifying if the tokens or credentials provided
by clients are valid before the requests reach the application.

Handling CORS: Middleware can determine which domains are allowed to access
your application's resources.

Request Modification: Middleware can modify requests by adding or altering headers 
before they reach the application.

Response Modification: Middleware can modify responses by providing custom headers, 
changing the response body, and so on.



If you have dependencies with yield, the exit code will run after the middleware.
If there were any background tasks (documented later), they will run after all the middleware.
"""

#MIDDLEWARE's can be functions or classes

from fastapi import FastAPI, Request
import time
import logging
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware


logger = logging.getLogger("uvicorn.access")
logger.disabled = True

def register_middleware(app : FastAPI):
    
    @app.middleware('http')
    async def custom_logging(request : Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        processing_time = time.time() - start_time
        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time}s"

        print(message)

        return response
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1" ,"0.0.0.0"],
    )
    
    """ @app.middleware('http')
    async def authorization(request : Request, call_next):
        if "Authorization" not in request.headers:
            #when using middleware you can not raise HTTP EXCEPTION
            return JSONResponse(
                content = {"message" : "Not Authenticated",
                           "resolution" : "Please provide the right credentials to proceed"
                           },
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        response = await call_next(request)
        return response """