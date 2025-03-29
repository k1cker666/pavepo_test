from fastapi import APIRouter, status


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.get("/ping", status_code=status.HTTP_200_OK)
async def ping():
    return {"ping": "pong"}