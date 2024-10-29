from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

from app.core.models import Parser


async def show_data(session: AsyncSession, user_id: int, skip: int, limit: int, filename: int):
    if "С_НДС" in filename:
        expectedColumns = ("best_price_without_nds", "best_price")
    elif "БЕЗ_НДС" in filename:
        expectedColumns = ("best_price", "best_price_with_nds")
    else:
        expectedColumns = ("best_price_without_nds", "best_price_with_nds")

    columns = [col for col in Parser.__table__.columns if col.name not in expectedColumns]
    stmt = select(*columns).where(Parser.user_id==user_id)
    result: Result = await session.execute(stmt)
    all_data = result.fetchall()

    return {
        "total": len(all_data),
        "rows": [dict(row._mapping) for row in all_data][skip:limit+skip]
    }