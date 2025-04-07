from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings import settings

engine = create_async_engine(url=settings.postgresql.get_conninfo())

new_session = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None, None]:
    async with new_session() as session:
        yield session

async def get_http_client() -> AsyncGenerator[AsyncClient, None, None]:
    async with AsyncClient() as client:
        yield client

http_client_dep = Annotated[AsyncClient, Depends(get_http_client)]
session_dep = Annotated[AsyncSession, Depends(get_session)]
