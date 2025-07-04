from math import ceil

import pandas as pd
import urllib.parse as up
import aiofiles

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

from app.core.models import File

from app.api_v1.auth.utils import get_payload


def create(df_to_list):
    return df_to_list[4:]

def split_file_for_thr(num: int, url: list) -> list[list]:
    '''
    num - число потоков # например 4
    url - список с url => [...] # 16 штук
    list[list] - список со списками url => [[...]] # 4 по 4 
    '''
    new_url = []
    step = ceil(len(url)/num)
    for i in range(0, len(url), step):
        if i+step > len(url)-1:
            new_url.append(url[i:])
        else:
            new_url.append(url[i:i+step])

    return new_url

def create_params_for_url(param: str):
    if "---" in param:
        param = param.replace("---", "+%2F+")
        return param
    if " / " in param:
        param = param.replace(" / ", "+%2F+")
        return param
    return up.quote(param)

def quick_sort(arr: list, index: int):
    '''
    Алгоритм быстрой сортировки
    arr - массив с массивами, которые будут сортироваться
    index - номер элемента (с 0) по которому мы с сортируем нашима массивы
    '''
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[len(arr) // 2][index]
        left = [x for x in arr if x[index] < pivot]
        middle = [x for x in arr if x[index] == pivot]
        right = [x for x in arr if x[index] > pivot]
        return quick_sort(left, index) + middle + quick_sort(right, index)

async def check_payload(access_token):
    try:
        payload = await get_payload(access_token=access_token)
    except Exception as e:
        raise e

    return payload

async def check_after_parsing_file(session: AsyncSession, user_id: int):
    stmt = select(File).where(File.user_id == user_id)
    result: Result = await session.execute(stmt)
    data = result.scalars().all()
    return data[-1].is_after_parsing if data != [] else False

async def create_empty_json(filepath: str):
    async with aiofiles.open(filepath, mode='w', encoding='utf-8') as f:
        await f.write('')

class ProxyException(Exception):
    def __init__(self, message):
        super().__init__(message)

