from fastapi import APIRouter, status

from app.db import Base
from app.deps import engine

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get(
    "/create_table",
    summary="Эндпоинт чтобы создать/пересоздать таблицы",
    description="Эндоинт для быстрого выполнения задачи, поэтому не защищен"
)
async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)