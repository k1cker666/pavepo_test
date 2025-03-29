from datetime import UTC, datetime, timedelta
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt

from app.settings import settings
from app.routers.auth.type import YandexToken
from app.routers.auth.schemas import YandexUser
from app.routers.auth.models import User


YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
YANDEX_USERINFO_URL = "https://login.yandex.ru/info"

def __get_data_for_token_request(code: str):
    return {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.yandex.client_id,
        "client_secret": settings.yandex.client_secret,
    }

async def get_token(code: str, http_client: AsyncClient) -> YandexToken:
    token_resp = await http_client.post(YANDEX_TOKEN_URL, data=__get_data_for_token_request(code))
    if token_resp.status_code != 200:
        raise HTTPException(
            status_code=token_resp.status_code,
            detail="Не удалось получить токен от Яндекса"
        )
    return YandexToken(**token_resp.json())

async def get_user_from_yandex(token: YandexToken, http_client: AsyncClient) -> YandexUser:
    headers = {"Authorization": f"OAuth {token.access_token}"}
    userinfo_resp = await http_client.get(YANDEX_USERINFO_URL, headers=headers)
    if userinfo_resp.status_code != 200:
        raise HTTPException(
            status_code=userinfo_resp.status_code,
            detail="Не удалось получить данные пользователя от Яндекса"
        )
    return YandexUser(**userinfo_resp.json())

async def get_user_by_yandex_id(session: AsyncSession, yandex_user: YandexUser) -> User | None:
    query = select(User).filter(User.yandex_id == yandex_user.yandex_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def create_user_by_yandex_info(session: AsyncSession, yandex_user: YandexUser) -> User:
    new_user = User(**yandex_user.model_dump())
    session.add(new_user)
    await session.commit()
    return new_user

def __create_token(user_yandex_id: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": user_yandex_id, "id": user_id}
    expires = datetime.now(UTC) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, settings.secret_key, algorithm=settings.algorithm)

def create_access_token(user_yandex_id: str, user_id: int):
    return __create_token(user_yandex_id, user_id, timedelta(minutes=20))

def create_refresh_token(user_yandex_id: str, user_id: int):
    return __create_token(user_yandex_id, user_id, timedelta(days=14))

def decode_token(token):
    return jwt.decode(token, settings.secret_key, algorithm=settings.algorithm)