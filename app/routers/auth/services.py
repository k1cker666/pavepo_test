from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
from fastapi import Cookie, Depends, HTTPException, status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from jose import ExpiredSignatureError, jwt, JWTError

from app.deps import session_dep
from app.settings import settings
from app.routers.auth.schemas import Credentials, YandexUser, YandexToken
from app.routers.auth.models import User


YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
YANDEX_USERINFO_URL = "https://login.yandex.ru/info"

def __get_data_for_token_request(code: str) -> dict:
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
    await session.refresh(new_user)
    return new_user

def __create_token(user_yandex_id: str, user_id: int, expires_delta: timedelta) -> str:
    encode = {"sub": user_yandex_id, "id": user_id}
    expires = datetime.now(UTC) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, settings.secret_key, algorithm=settings.algorithm)

def create_access_token(user_yandex_id: str, user_id: int) -> str:
    return __create_token(user_yandex_id, user_id, timedelta(minutes=20))

def create_refresh_token(user_yandex_id: str, user_id: int) -> str:
    return __create_token(user_yandex_id, user_id, timedelta(days=14))

def decode_token(token) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

def is_token_expired(token: str) -> bool:
    try:
        payload = decode_token(token)
        if datetime.fromtimestamp(payload.get('exp'), UTC) > datetime.now(UTC):
            return False
        return True
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ошибка валидации пользователя")

async def get_current_user(session: AsyncSession, token: str) -> User:
    try:
        payload = decode_token(token)
        user_yandex_id = payload.get("sub")
        if not user_yandex_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ошибка валидации пользователя")
        query = select(User).filter(User.yandex_id == user_yandex_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не зарегестрирован")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный payload")

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

async def set_username_and_password(
    session: AsyncSession,
    credentials: Credentials,
    current_user: User
) -> None:
    try:
        current_user.username = credentials.username
        current_user.hashed_password = hash_password(credentials.password)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username уже существует"
        )

async def authenticate_user(
    session: AsyncSession,
    username: str,
    password: str,
) -> User:
    query = select(User).filter(User.username == username)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не существует"
        )
    if not check_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Имя пользователя или пароль неверны"
        )
    return user

def get_current_refresh_token_payload(
    refresh_token: str = Cookie(None)
) -> dict:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не найден"
        )
    try:
        payload = decode_token(refresh_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Токен истек"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не валиден"
        )
    return payload

async def get_auth_user_for_refresh(
    refresh_token_payload: Annotated[dict, Depends(get_current_refresh_token_payload)],
    session: session_dep,
):
    if not (sub := refresh_token_payload.get("sub")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credentials не переданы"
        )

    query = select(User).filter(User.yandex_id == sub)
    result = await session.execute(query)
    if not (user := result.scalar_one_or_none()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    return user