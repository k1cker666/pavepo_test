from fastapi import FastAPI, status
from starlette.middleware.sessions import SessionMiddleware

from app.routers.auth.auth import router as auth_router
from app.settings import settings

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key
)

app.include_router(auth_router)


@app.get("/ping", status_code=status.HTTP_200_OK, tags=["test"])
async def ping():
    return {"ping": "pong"}
