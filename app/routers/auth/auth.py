from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.deps import http_client_dep, session_dep
from app.routers.auth.models import User
from app.routers.auth.schemas import AccessToken, Credentials
from app.routers.auth.services import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    create_user_by_yandex_info,
    get_auth_user_for_refresh,
    get_current_user,
    get_token,
    get_user_by_yandex_id,
    get_user_from_yandex,
    is_token_expired,
    set_username_and_password,
)
from app.settings import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get(
    "/yandex",
    summary="Получаем код от яндекса.",
    description="Перенаправление пользователя на страницу авторизации Яндекса.",
)
def yandex_auth() -> RedirectResponse:
    yandex_authrize_url = settings.yandex.authrize_url
    auth_url = yandex_authrize_url.format(settings.yandex.client_id, settings.yandex.redirect_uri)
    return RedirectResponse(auth_url)


@router.get(
    "/yandex/callback",
    summary="Обрабатываем код",
    description=(
    "- Меняем код на acceess_token\n"
    "- Запрашиваем информацию о пользователе\n"
    "- Генерируем внутренние JWT токены"
    ),
    status_code=status.HTTP_200_OK,
)
async def yandex_callback(
    code: str,
    http_client: http_client_dep,
    session: session_dep,
    response: Response,
) -> AccessToken:
    token = await get_token(code, http_client)
    if not token.access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ответ не содержит access_token")

    yandex_user = await get_user_from_yandex(token, http_client)

    existing_user = await get_user_by_yandex_id(session, yandex_user)
    if existing_user:
        user = existing_user
    else:
        user = await create_user_by_yandex_info(session, yandex_user)

    access_token = create_access_token(user.yandex_id, user.id)
    refresh_token = create_refresh_token(user.yandex_id, user.id)

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    return AccessToken(access_token=access_token)

@router.post(
    "/set_credentials",
    summary="Устанавливаем пользователю данные для входы",
    status_code=status.HTTP_200_OK,
)
async def set_credentials(
    credentials: Credentials,
    request: Request,
    session: session_dep,
) -> JSONResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh_token не найден")
    if is_token_expired(refresh_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Refresh_token истек")

    current_user = await get_current_user(session, refresh_token)

    await set_username_and_password(session, credentials, current_user)
    return JSONResponse({"message": "Username и password установлены"})

@router.post(
    "/token",
    summary="Выпускаем access_token",
    status_code=status.HTTP_200_OK,
)
async def login_for_access_token(
    session: session_dep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
) -> AccessToken:
    user = await authenticate_user(session, form_data.username, form_data.password)

    access_token = create_access_token(user.yandex_id, user.id)
    refresh_token = create_refresh_token(user.yandex_id, user.id)

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    return AccessToken(access_token=access_token)

@router.post(
    "/token/refresh",
    summary="Обновляем access_token",
)
async def refresh_token(user: Annotated[User, Depends(get_auth_user_for_refresh)]) -> AccessToken:
    access_token = create_access_token(user.yandex_id, user.id)
    return AccessToken(access_token=access_token)
