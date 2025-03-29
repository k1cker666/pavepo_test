from fastapi import FastAPI, status
from starlette.middleware.sessions import SessionMiddleware

from app.routers.auth.auth import router as auth_router
from app.settings import settings
from app.db import Base
from app.deps import engine

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key
)

app.include_router(auth_router)


@app.get("/ping", status_code=status.HTTP_200_OK, tags=["test"])
async def ping():
    return {"ping": "pong"}

@app.get("/create_table")
async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)