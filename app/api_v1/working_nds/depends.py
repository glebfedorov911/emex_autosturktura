from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

from app.core.models import Parser, File
from app.core.config import settings

import pandas as pd


async def get_all_data_from_file(file_id: int, user_id: int, session: AsyncSession):
    stmt = select(Parser).where(Parser.user_id==user_id).where(Parser.file_id==file_id)
    result: Result = await session.execute(stmt)
    parsers_data = result.scalars().all()
    if parsers_data == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У юзера нет такого файла"
        )

    return parsers_data

def edit_price(data):
    if data.best_price.lower() == "пусто":
        return None

    if data.nds.lower() == "нет":
        price_company = int(float(data.price) * 1.07)
        price_from_site = int(data.best_price)

        if price_company < price_from_site:
            best_price = price_from_site - 1
        else:
            best_price = price_company
    else:
        price_company = int(float(data.price) * 1.27)
        price_from_site = int(data.best_price)
        if price_company < price_from_site:
            best_price = price_from_site - 1
        else:
            best_price = price_company
    
    return best_price

async def get_file(file_id: int, session: AsyncSession, user_id: int):
    stmt = select(File).where(File.id==file_id).where(File.user_id==user_id)
    result: Result = await session.execute(stmt)
    file = result.scalar()
    
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У юзера нет такого файла"
        ) 

    return file

async def get_filename(file_id: int, session: AsyncSession, user_id: int):
    file = await get_file(file_id=file_id, user_id=user_id, session=session)
    return file.after_parsing_filename

async def set_filename(file_id: int, session: AsyncSession, user_id: int):
    file = await get_file(file_id=file_id, user_id=user_id, session=session)

    file.after_parsing_filename = f"обработанный_{file.after_parsing_filename}"
    session.add(file)
    await session.commit()

async def to_file(filename: str, parser_data: list):
    columns = ["Артикул", "Наименование", "Брэнд", "Артикул", "Кол-во", "Цена", "Партия", "НДС", "Лого", "Доставка", "Лучшая цена", "Количество"]
    if parser_data[0].new_price:
        columns.append("Цена с лого")
    excel = [[data.article, data.name, data.brand, data.article1, data.quantity, data.price, data.batch, data.nds, data.logo, data.delivery_time, data.best_price, data.quantity1, data.new_price] if data.new_price else [data.article, data.name, data.brand, data.article1, data.quantity, data.price, data.batch, data.nds, data.logo, data.delivery_time, data.best_price, data.quantity1] for data in parser_data ]
    df = pd.DataFrame(excel, columns=columns)
    df.to_excel(str(settings.upload.path_for_upload) + "/" + f"обработанный_{filename}", index=False)

