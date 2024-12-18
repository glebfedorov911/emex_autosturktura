from fastapi import HTTPException, status
from fastapi.responses import FileResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

from app.core.models import File, Parser
from app.core.config import settings
from .schemas import FilesCreate
from .depends import get_files, zero_files, check_has_last_file_after_parsing, edit_file

import pandas as pd
import os


async def create_file_in_db(session: AsyncSession, user_id: int, filename: str):
    files = FilesCreate(user_id=user_id, before_parsing_filename=filename, filename_after_parsing=f"ПОСЛЕ_ПАРСИНГА_{filename}", 
    filename_after_parsing_without_nds=f"ПОСЛЕ_ПАРСИНГА_БЕЗ_НДС_{filename}", 
    filename_after_parsing_with_nds=f"ПОСЛЕ_ПАРСИНГА_С_НДС_{filename}")
    new_file = File(**files.model_dump())
    session.add(new_file)
    await session.commit()
    
async def get_last_file(session: AsyncSession, user_id: int):
    files = await get_files(session=session, user_id=user_id)
    zero_files(files)
    last_file = files[-1]
    return last_file

async def get_files_by_user_id(session: AsyncSession, user_id: int):
    files = await get_files(session=session, user_id=user_id)
    zero_files(files)
    return files

async def get_files_by_id(session: AsyncSession, file_id: int):
    stmt = select(File).where(File.id == file_id)
    result: Result = await session.execute(stmt)
    files = result.scalars().all()
    zero_files(files)

    return files[0]

async def get_file_by_ids(session: AsyncSession, file_ids: list[int]):
    stmt = select(File).where(File.id.in_(file_ids))
    result: Result = await session.execute(stmt)
    return result.scalars().all()

async def getDataForCreateFile(session: AsyncSession, file_id: int, nds: bool = None):
    stmt = select(Parser).where(Parser.file_id==file_id)
    result: Result = await session.execute(stmt)
    dataFromParsing = result.scalars().all()
    columns = ["Код товара", "Артикул", "Наименование", "Брэнд", "Артикул", "Кол-во", "Цена", "Цена ABCP", "Партия", "Лого", "Доставка", "Лучшая цена", "Количество"]
    if not dataFromParsing[0].new_price is None:
        columns.append("Цена с лого")
    if nds is None:
        if dataFromParsing[0].new_price:
            return columns, [[row.good_code, row.article, row.name, row.brand, row.article1, row.quantity, row.price, row.abcp_price, row.batch, row.logo, row.delivery_time, row.best_price, row.quantity1, row.new_price] for row in dataFromParsing]
        return columns, [[row.good_code, row.article, row.name, row.brand, row.article1, row.quantity, row.price, row.abcp_price, row.batch, row.logo, row.delivery_time, row.best_price, row.quantity1] for row in dataFromParsing]
    if not nds:
        if dataFromParsing[0].new_price:
            return columns, [[row.good_code, row.article, row.name, row.brand, row.article1, row.quantity, row.price, row.abcp_price, row.batch, row.logo, row.delivery_time, row.best_price_without_nds, row.quantity1, row.new_price] for row in dataFromParsing]
        return columns, [[row.good_code, row.article, row.name, row.brand, row.article1, row.quantity, row.price, row.abcp_price, row.batch, row.logo, row.delivery_time, row.best_price_without_nds, row.quantity1] for row in dataFromParsing]
    else:
        if dataFromParsing[0].new_price:
            return columns, [[row.good_code, row.article, row.name, row.brand, row.article1, row.quantity, row.price, row.abcp_price, row.batch, row.logo, row.delivery_time, row.best_price_with_nds, row.quantity1, row.new_price] for row in dataFromParsing]
        return columns, [[row.good_code, row.article, row.name, row.brand, row.article1, row.quantity, row.price, row.abcp_price, row.batch, row.logo, row.delivery_time, row.best_price_with_nds, row.quantity1] for row in dataFromParsing]

async def create_file(session: AsyncSession, file_id: int, filestart: str, nds: bool = None):
    filename = await get_files_by_id(session=session, file_id=file_id)
    check_has_last_file_after_parsing(filename)
    result_file_name = f"{filestart}_{filename.before_parsing_filename}"
    if not os.path.exists(filepath := os.path.join(settings.upload.path_for_upload, result_file_name)):
        headerFile, dataForCreatingFile = await getDataForCreateFile(session=session, file_id=file_id, nds=nds)
        df = pd.DataFrame(dataForCreatingFile, columns=headerFile)
        df.to_excel(
            filepath,
            index=False,
        )
        await edit_file(filepath, ["F", "G", "I", "J", "K", "L", "M", "N"])
    return FileResponse(path=filepath, filename=result_file_name)

async def delete_files(session: AsyncSession, user_id: int, file_ids: list[int]):
    files = await get_file_by_ids(session=session, file_ids=file_ids)
    for file in files:
        if file.before_parsing_filename and os.path.exists(os.path.join(settings.upload.path_for_upload, file.before_parsing_filename)):
            os.remove(os.path.join(settings.upload.path_for_upload, file.before_parsing_filename))
        if file.filename_after_parsing and os.path.exists(os.path.join(settings.upload.path_for_upload, file.filename_after_parsing)):
            os.remove(os.path.join(settings.upload.path_for_upload, file.filename_after_parsing))
        if file.filename_after_parsing_with_nds and os.path.exists(os.path.join(settings.upload.path_for_upload, file.filename_after_parsing_with_nds)):
            os.remove(os.path.join(settings.upload.path_for_upload, file.filename_after_parsing_with_nds))
        if file.filename_after_parsing_without_nds and os.path.exists(os.path.join(settings.upload.path_for_upload, file.filename_after_parsing_without_nds)):
            os.remove(os.path.join(settings.upload.path_for_upload, file.filename_after_parsing_without_nds))
        await session.delete(file)
    await session.commit()

    return await get_files(session=session, user_id=user_id)