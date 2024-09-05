from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

from app.core.models import Parser


async def show_data(session: AsyncSession, user_id: int, skip: int, limit: int, file_id: int):
    stmt = select(Parser).where(Parser.user_id==user_id).where(Parser.file_id==file_id).offset(skip).limit(limit)
    result: Result = await session.execute(stmt)
    data = result.scalars().all()

    return {
        "total": len(data),
        "rows": data
    }