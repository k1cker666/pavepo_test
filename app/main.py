from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.settings import settings
from app.routers.auth.auth import router as auth_router
from app.routers.users.users import router as users_router
from app.routers.audio.audio import router as audio_router
from app.routers.admin.admin import router as admin_router

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key
)

app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(audio_router)