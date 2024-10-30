from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

from app.core.models import Parser, File


async def show_data(session: AsyncSession, user_id: int, skip: int, limit: int, filename: int):
    if "С_НДС" in filename:
        expectedColumns = ("best_price_without_nds", "best_price")
        stmt = select(File).where(File.filename_after_parsing_with_nds==filename)
    elif "БЕЗ_НДС" in filename:
        expectedColumns = ("best_price", "best_price_with_nds")
        stmt = select(File).where(File.filename_after_parsing_without_nds==filename)
    else:
        expectedColumns = ("best_price_without_nds", "best_price_with_nds")
        stmt = select(File).where(File.filename_after_parsing==filename)

    result: Result = await session.execute(stmt)
    files = result.scalars().all()

    columns = [col for col in Parser.__table__.columns if col.name not in expectedColumns]
    stmt = select(*columns).where(Parser.user_id==user_id).where(Parser.file_id==files[-1].id)
    result: Result = await session.execute(stmt)
    all_data = result.fetchall()

    return {
        "total": len(all_data),
        "rows": [dict(row._mapping) for row in all_data][skip:limit+skip]
    }