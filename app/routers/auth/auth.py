from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from httpx import AsyncClient

from app.settings import settings
from app.deps import http_client_dep

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

YANDEX_AUTHRIZE_URL = "https://oauth.yandex.ru/authorize?response_type=code&client_id={}&redirect_uri={}"
YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
YANDEX_USERINFO_URL = "https://login.yandex.ru/info"


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
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.yandex.client_id,
        "client_secret": settings.yandex.client_secret,
    }

    token_resp = await http_client.post(YANDEX_TOKEN_URL, data=data)
    if token_resp.status_code != 200:
        raise HTTPException(
            status_code=token_resp.status_code,
            detail="Не удалось получить токен от Яндекса"
        )

    token_json = token_resp.json()
    access_token = token_json.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Ответ не содержит access_token")

    headers = {"Authorization": f"OAuth {access_token}"}
    userinfo_resp = await http_client.get(YANDEX_USERINFO_URL, headers=headers)
    if userinfo_resp.status_code != 200:
        raise HTTPException(
            status_code=userinfo_resp.status_code,
            detail="Не удалось получить данные пользователя от Яндекса"
        )
    user_info = userinfo_resp.json()

    return JSONResponse({
        "user_info": user_info,
        "yandex_access_token": access_token
    })