import os
from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.audio.models import AudioFile
from app.routers.auth.models import User

async def make_user_admin(
    session: AsyncSession,
    user: User
) -> None:
    user.is_admin = True
    await session.commit()

async def delete_user_by_id(
    session: AsyncSession,
    user_id: int
) -> None:
    query = select(AudioFile).filter(AudioFile.user_id == user_id)
    result = await session.execute(query)
    audio_files = result.scalars().all()

    delete_users_files(audio_files)

    query = delete(User).filter(User.id == user_id)
    await session.execute(query)
    await session.commit()

def delete_users_files(
    audio_files: Sequence[AudioFile]
) -> None:
    if not audio_files:
        return
    for audio_file in audio_files:
        os.remove(audio_file.path)