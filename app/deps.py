from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient

async def get_http_client():
    async with AsyncClient() as client:
        yield client

http_client_dep = Annotated[AsyncClient, Depends(get_http_client)]