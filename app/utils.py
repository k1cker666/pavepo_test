from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from jose.exceptions import ExpiredSignatureError, JWTError

from app.deps import session_dep
from app.routers.auth.services import decode_token
from app.routers.auth.models import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
)

def get_current_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)] 
) -> dict:
    try:
        payload = decode_token(token)
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

async def get_current_auth_user(
    payload: Annotated[dict, Depends(get_current_token_payload)],
    session: session_dep,
) -> User:
    if not (sub := payload.get("sub")):
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

async def get_current_auth_admin(
    user: Annotated[User, Depends(get_current_auth_user)]
) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав админа"
        )
    return user