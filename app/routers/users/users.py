from typing import Annotated
from fastapi import APIRouter, Depends

from app.utils import get_current_user
from app.routers.auth.models import User
from app.routers.auth.schemas import UserSchema

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/me", summary="Информация об авторизированном пользователе")
async def get_auth_user_info(user: Annotated[User, Depends(get_current_user)]):
    return UserSchema.model_validate(user)

# @router.put(
#     "/me",
#     summary="Обновление данных",
#     description=(
#         "Поменять можно только: имя, фамилию, пол"
#     )
# )