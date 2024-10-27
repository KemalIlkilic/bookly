from fastapi import FastAPI
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from src.auth.routes import auth_router

#alembic olmadan önce table ları olusturmak icin önemli olan bir mevzu.
@asynccontextmanager
async def life_span(app : FastAPI):
    #doing smth after server start
    print("Server is starting...")
    await init_db()
    yield
    #doing smth before server end
    print("Server is ending...")


version = "v1"

app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version=version
    #lifespan=life_span ,no more needed
)

app.include_router(book_router ,prefix=f"/api/{version}/books", tags=['books'])
app.include_router(auth_router ,prefix=f"/api/{version}/auth", tags=['auth'])

