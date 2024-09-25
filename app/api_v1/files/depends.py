from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

from app.core.models import File

import os
import pandas as pd


async def get_files(session: AsyncSession, user_id: int):
    stmt = select(File).where(File.user_id==user_id).order_by(File.date)
    result: Result = await session.execute(stmt)
    files = result.scalars().all()

    return files

def zero_files(files):
    if files == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файлов нет у данного пользователя"
        )

def check_same(file):
    try:
        RIGHT_DATA = [i for i in pd.read_excel("app/upload_file/shablon.xlsx").values.tolist() if "Артикул" in i][0]
        RIGHT_DATA = [i for i in RIGHT_DATA if str(i) != "nan"]
        df = [i for i in pd.read_excel(file).values.tolist() if "Артикул" in i][0]
        df = [i for i in df if str(i) != "nan"]
    except:
        return False

    return list(df) == RIGHT_DATA 

def check_has_last_file_after_parsing(last_file):
    if last_file.after_parsing_filename is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Последний файл еще не спаршен"
        )