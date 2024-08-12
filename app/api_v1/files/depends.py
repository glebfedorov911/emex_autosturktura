from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

from app.core.models import File

import os
import pandas as pd


def get_unique_filename(directory, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(directory, unique_filename)):
        unique_filename = f"{base}_({counter}){extension}"
        counter += 1

    return unique_filename

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
    RIGHT_DATA = list(pd.read_excel("app/upload_file/shablon.xlsx"))

    df = pd.read_excel(file)

    return list(df) == RIGHT_DATA 