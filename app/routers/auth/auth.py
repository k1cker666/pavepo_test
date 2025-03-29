from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import RedirectResponse

from app.settings import settings
from app.deps import http_client_dep, session_dep
from app.routers.auth.schemas import AccessToken
from app.routers.auth.services import (
    get_token,
    get_user_from_yandex,
    get_user_by_yandex_id,
    create_user_by_yandex_info,
    create_access_token,
    create_refresh_token
)

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


@router.post(
    "/yandex/callback",
    summary="Обрабатываем код",
    description=(
    "- Меняем код на acceess_token\n"
    "- Запрашиваем информацию о пользователе\n"
    "- Генерируем внутренние JWT токены"
    ),
    status_code=status.HTTP_200_OK
)
async def yandex_callback(
    code: str,
    http_client: http_client_dep,
    session: session_dep,
    response: Response
) -> AccessToken:
    token = await get_token(code, http_client)
    if not token.access_token:
        raise HTTPException(status_code=400, detail="Ответ не содержит access_token")

    yandex_user = await get_user_from_yandex(token, http_client)

    existing_user = await get_user_by_yandex_id(session, yandex_user)
    if existing_user:
        user = existing_user
    else:
        user = await create_user_by_yandex_info(session, yandex_user)

    access_token = create_access_token(user.yandex_id, user.id)
    refresh_token = create_refresh_token(user.yandex_id, user.id)

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return {"access_token": access_token, "token_type": "bearer"}
