from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.db import Base
from app.deps import engine, session_dep
from app.routers.admin.services import delete_user_by_id, make_user_admin
from app.routers.auth.models import User
from app.utils import get_current_auth_admin, get_current_auth_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@router.get(
    "/create_table",
    summary="Эндпоинт чтобы создать/пересоздать таблицы",
    description=(
        "Эндоинт для быстрого выполнения задачи, поэтому не защищен\n"
        "Нужно использовать перед использованием сервиса"
    ),
)
async def create_table() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@router.post(
    "/make_admin",
    summary="Эндпоинт делает из пользователя админа",
)
async def make_admin(
    session: session_dep,
    user: Annotated[User, Depends(get_current_auth_user)],
) -> JSONResponse:
    await make_user_admin(session, user)
    return JSONResponse({"message": "Теперь ты админ"})

@router.delete(
    "/delete_user/{user_id}",
    summary="Удаление пользователя из базы",
    description="Для использования нужно иметь права админа",
)
async def delete_user(
    user_id: int,
    session: session_dep,
    admin: Annotated[User, Depends(get_current_auth_admin)], # noqa: ARG001
) -> JSONResponse:
    await delete_user_by_id(session, user_id)
    return JSONResponse({"message": f"Пользователь с id {user_id} удален"})
