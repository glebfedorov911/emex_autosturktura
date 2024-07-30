from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import db_helper
from app.core.config import settings
from app.api_v1.users.crud import get_payload
from . import crud
from .depends import get_unique_filename

import os


router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/upload_file/")
async def upload_file(file: UploadFile = File(...), session: AsyncSession = Depends(db_helper.session_depends), payload = Depends(get_payload)):
    directory = settings.upload.path_for_upload
    unique_filename = get_unique_filename(directory, file.filename)
    file_location = os.path.join(directory, unique_filename)

    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    await crud.create_file_in_db(session=session, user_id=payload.get("sub"), filename=unique_filename)

    return {
        "message": f"Файл {unique_filename} сохранен по пути {file_location}"
    }

@router.post("/download_file/")
async def download_file(session: AsyncSession = Depends(db_helper.session_depends), payload=Depends(get_payload)):
    last_file = await crud.get_last_file(session=session, user_id=payload.get("sub"))
    file_location = os.path.join(settings.upload.path_for_upload, last_file.filename)
    return FileResponse(path=file_location, filename=last_file.filename)

@router.post("/download_file/{filename}")
async def download_file(filename: str, session: AsyncSession = Depends(db_helper.session_depends), payload=Depends(get_payload)):
    file_location = os.path.join(settings.upload.path_for_upload, filename)
    if not os.path.exists(file_location):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет такого файла"
        )
    return FileResponse(path=file_location, filename=filename)

@router.get("/all_files/")
async def get_files(session: AsyncSession = Depends(db_helper.session_depends), payload=Depends(get_payload)):
    return await crud.get_files_by_user_id(session=session, user_id=payload.get("sub"))