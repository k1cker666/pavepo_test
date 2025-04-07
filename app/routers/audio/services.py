from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import Sequence, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.audio.models import AudioFile
from app.routers.auth.models import User
from app.settings import settings


async def get_list_audio_files(
    session: AsyncSession,
    user: User,
) -> Sequence[AudioFile]:
    query = select(AudioFile).filter(AudioFile.user == user)
    result = await session.execute(query)
    return result.scalars().all()

async def upload_file(
    session: AsyncSession,
    user: User,
    file: UploadFile,
    file_name: str,
) -> AudioFile:
    if not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно загружать только аудио файлы",
        )
    try:
        extension = Path(file.filename).suffix
        new_name = file_name+extension
        file_location = settings.audio_storage_path / new_name

        new_audio = AudioFile(
            name = new_name,
            path = file_location,
            user_id = user.id,
        )
        session.add(new_audio)
        await session.commit()

        async with aiofiles.open(file_location, "wb") as output_file:
            while chunk := await file.file.read(1024):
                await output_file.write(chunk)

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такое имя уже существует",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Файл не удалось сохранить",
        )
    await session.refresh(new_audio)
    return new_audio

async def get_file_by_id(
    session: AsyncSession,
    file_id: int,
    user: User,
) -> AudioFile:
    query = select(AudioFile).filter(AudioFile.id == file_id).filter(AudioFile.user == user)
    result = await session.execute(query)
    audio_file = result.scalar_one_or_none()
    if not audio_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл не существует",
        )
    return audio_file
