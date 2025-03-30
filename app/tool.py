import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from db import Base
from settings import settings


async def create_tables():
    engine = create_async_engine(url=settings.postgresql.get_conninfo(), echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())