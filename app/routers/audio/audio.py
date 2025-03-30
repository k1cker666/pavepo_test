from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.deps import session_dep
from app.routers.audio.models import AudioFile
from app.routers.audio.schemas import AudioSchema
from app.routers.auth.models import User
from app.utils import get_current_auth_user


router = APIRouter(
    prefix="/audio",
    tags=["audio"]
)

@router.get(
    "/audio"
)
async def get_user_audio_list(
    session: session_dep,
    user: Annotated[User, Depends(get_current_auth_user)]
):
    query = select(AudioFile).filter(AudioFile.user == user)
    result = await session.execute(query)
    audio = result.scalars().all()
    return [AudioSchema.model_dump(audio_) for audio_ in audio]