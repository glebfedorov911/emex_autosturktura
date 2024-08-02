from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

from app.core.models import File
from .schemas import FilesCreate
from .depends import get_files, zero_files


async def create_file_in_db(session: AsyncSession, user_id: int, filename: str):
    files = FilesCreate(user_id=user_id, before_parsing_filename=filename)
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

async def get_files_by_id(session: AsyncSession, user_id: int, file_id: int):
    stmt = select(File).where(File.user_id==user_id).where(File.id == file_id)
    result: Result = await session.execute(stmt)
    files = result.scalars().all()
    zero_files(files)

    return files[0]