from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

from app.settings import settings
from app.deps import http_client_dep
from app.routers.auth.services import get_token, get_user_from_yandex

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

YANDEX_AUTHRIZE_URL = "https://oauth.yandex.ru/authorize?response_type=code&client_id={}&redirect_uri={}"


@router.get(
    "/yandex",
    summary="Получаем код от яндекса.",
    description="Перенаправление пользователя на страницу авторизации Яндекса.",
)
def yandex_auth():
    auth_url = YANDEX_AUTHRIZE_URL.format(settings.yandex.client_id, settings.yandex.redirect_uri)
    return RedirectResponse(auth_url)


@router.get(
    "/yandex/callback",
    summary="Обрабатываем код",
    description=(
    "- Меняем код на acceess_token\n"
    "- Запрашиваем информацию о пользователе"
    ),
)
async def yandex_callback(code: str, http_client: http_client_dep):
    token = await get_token(code, http_client)
    if not token.access_token:
        raise HTTPException(status_code=400, detail="Ответ не содержит access_token")
    yandex_user = await get_user_from_yandex(token, http_client)
    return JSONResponse({
        "user_info": yandex_user.model_dump(),
        "yandex_access_token": token.access_token
    })
