from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Header
from fastapi.responses import FileResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import db_helper
from app.core.config import settings
from app.api_v1.auth.utils import get_payload
from . import crud
from .depends import check_same, check_has_last_file_after_parsing
from app.api_v1.utils.depends import get_unique_filename, get_shablon as gs

import os
import pandas as pd


router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/upload_file")
async def upload_file(file: UploadFile = File(...), session: AsyncSession = Depends(db_helper.session_depends), payload = Depends(get_payload)):
    
    directory = settings.upload.path_for_upload
    # unique_filename = get_unique_filename(directory, f"{payload.get('username')}_дляпарсинг.{file.filename.split('.')[-1]}")
    unique_filename = get_unique_filename(directory, file.filename)
    # unique_filename = get_unique_filename(directory, f"{payload.get("username")}_дляпарсинг.xlsx")
    file_location = os.path.join(directory, unique_filename)

    if file.filename.split('.')[-1] not in ("xlsx", "xls"):
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Неподходящий формат файла"
        )

    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    if not check_same(file_location):
        os.remove(file_location)
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Файл не по шаблону"
        )

    await crud.create_file_in_db(session=session, user_id=payload.get("sub"), filename=unique_filename)

    return {
        "message": f"Файл {unique_filename} сохранен по пути {file_location}"
    }


@router.get("/download_file/before_parsing/{file_id}")
async def download_file(file_id: int, session: AsyncSession = Depends(db_helper.session_depends)):
    filename = await crud.get_files_by_id(session=session, file_id=file_id)
    file_location = os.path.join(settings.upload.path_for_upload, filename.before_parsing_filename)
    if not os.path.exists(file_location):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет такого файла"
        )
    return FileResponse(path=file_location, filename=filename.before_parsing_filename)

@router.get("/download_file/after_parsing/{file_id}")
async def download_file(file_id: int, session: AsyncSession = Depends(db_helper.session_depends)):
    try:
        return await crud.create_file(session=session, file_id=file_id, filestart="ПОСЛЕ_ПАРСИНГА")
    except:
        return HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="Файл еще не начал парситься"
        )

@router.get("/download_file/after_parsing_without_nds/{file_id}")
async def download_file(file_id: int, session: AsyncSession = Depends(db_helper.session_depends)):
    try:
        return await crud.create_file(session=session, file_id=file_id, filestart="ПОСЛЕ_ПАРСИНГА_БЕЗ_НДС", nds=False)
    except:
        return HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="Файл еще не начал парситься"
        )

@router.get("/download_file/after_parsing_with_nds/{file_id}")
async def download_file(file_id: int, session: AsyncSession = Depends(db_helper.session_depends)):
    try:
        return await crud.create_file(session=session, file_id=file_id, filestart="ПОСЛЕ_ПАРСИНГА_C_НДС", nds=True)
    except:
        return HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="Файл еще не начал парситься"
        )
        
@router.get("/all_files")
async def get_files(session: AsyncSession = Depends(db_helper.session_depends), payload = Depends(get_payload)):
    return await crud.get_files_by_user_id(session=session, user_id=payload.get("sub"))

@router.get("/get_shablon")
async def get_shablon():
    return await gs(settings.upload.path_for_upload)

@router.delete("/delete_files")
async def delete_file(file_ids: list[int], payload = Depends(get_payload), session: AsyncSession = Depends(db_helper.session_depends)):
    return await crud.delete_files(session=session, user_id=payload.get("sub"), file_ids=file_ids)