from typing import Annotated
from fastapi import APIRouter, Depends, status

from app.deps import session_dep
from app.utils import get_current_auth_user
from app.routers.auth.models import User
from app.routers.auth.schemas import UserSchema
from app.routers.users.schemas import UserUpdate
from app.routers.users.services import update_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get(
    "/me",
    summary="Информация об авторизированном пользователе",
    response_model=UserSchema,
    status_code=status.HTTP_200_OK
)
async def get_auth_user_info(user: Annotated[User, Depends(get_current_auth_user)]):
    return UserSchema.model_validate(user)

@router.patch(
    "/me",
    summary="Обновление данных пользователя",
    description=(
        "Поменять можно только: имя, фамилию, пол"
    ),
    response_model=UserSchema,
    status_code=status.HTTP_200_OK
)
async def update_user_info(
    user: Annotated[User, Depends(get_current_auth_user)],
    user_update: UserUpdate,
    session: session_dep,
):
    updated_user = await update_user(session, user, user_update)
    return UserSchema.model_validate(updated_user)