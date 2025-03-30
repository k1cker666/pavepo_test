from typing import Annotated, List
from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse

from app.deps import session_dep
from app.routers.audio.schemas import AudioSchema
from app.routers.audio.services import get_file_by_id, get_list_audio_files, upload_file
from app.routers.auth.models import User
from app.utils import get_current_auth_user

router = APIRouter(
    prefix="/audio",
    tags=["audio"]
)

@router.get(
    "/",
    response_model=List[AudioSchema],
    summary="Получение списка загруженных аудиофайлов пользователем",
    status_code=status.HTTP_200_OK
)
async def get_file_list(
    session: session_dep,
    user: Annotated[User, Depends(get_current_auth_user)]
):
    audio = await get_list_audio_files(session, user)
    return [AudioSchema.model_validate(audio_) for audio_ in audio]

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=AudioSchema,
    summary="Загрузка аудио файла",
    description="В новом названии расширение передавать не нужно"
)
async def upload_audio_file(
    session: session_dep,
    file_name: str,
    user: Annotated[User, Depends(get_current_auth_user)],
    file: UploadFile = File(...),
):
    audio_file = await upload_file(session, user, file, file_name)
    return AudioSchema.model_validate(audio_file)

@router.get(
    "/{file_id}",
    status_code=status.HTTP_200_OK,
    summary="Скачать загруженный файл"
)
async def get_audio_file(
    session: session_dep,
    file_id: int,
    user: Annotated[User, Depends(get_current_auth_user)],
):
    file = await get_file_by_id(session, file_id, user)
    return FileResponse(file.path, media_type="audio/mpeg", filename=file.name)