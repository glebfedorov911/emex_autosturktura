from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

from app.core.models import Parser
from .schemas import ParserCreate
from .depends import *


async def edit_with_nds(session: AsyncSession, user_id: int, file_id: int):
    parsers_data = await get_all_data_from_file(session=session, user_id=user_id, file_id=file_id)

    for data in parsers_data:
        best_price = edit_price(data)
        if not best_price:
            continue
        
        data.best_price = str(best_price)
        session.add(data)
        await session.commit()
    
    filename = await get_filename(file_id=file_id, user_id=user_id, session=session)
    try:
        await to_file(filename=filename, parser_data=await get_all_data_from_file(session=session, user_id=user_id, file_id=file_id))
    except:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Невозможно сохранить"
        ) 
    await set_filename(file_id=file_id, session=session, user_id=user_id)

    return parsers_data