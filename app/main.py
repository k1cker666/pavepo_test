from fastapi import FastAPI, status
from routers.auth.auth import router as auth_router

app = FastAPI()

app.include_router(auth_router)


@app.get("/ping", status_code=status.HTTP_200_OK)
async def ping():
    return {"ping": "pong"}