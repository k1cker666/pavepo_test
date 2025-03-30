import os
import shutil
from fastapi import UploadFile, HTTPException, status
from sqlalchemy import Sequence, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import settings
from app.routers.audio.models import AudioFile
from app.routers.auth.models import User


async def get_list_audio_files(
    session: AsyncSession,
    user: User,
) -> Sequence[AudioFile]:
    query = select(AudioFile).filter(AudioFile.user == user)
    result = await session.execute(query)
    audio = result.scalars().all()
    return audio

async def upload_file(
    session: AsyncSession,
    user: User,
    file: UploadFile,
    file_name: str,
) -> AudioFile:
    if not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно загружать только аудио файлы"
        )
    try:
        _, extension = os.path.splitext(file.filename)
        new_name = file_name+extension
        file_location = os.path.join(settings.audio_storage_path, new_name)

        new_audio = AudioFile(
            name = new_name,
            path = file_location,
            user_id = user.id
        )
        session.add(new_audio)
        await session.commit()

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такое имя уже существует"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Файл не удалось сохранить"
        )
    await session.refresh(new_audio)
    return new_audio
