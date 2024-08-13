from fastapi import HTTPException, status

from playwright.async_api import async_playwright, TimeoutError as playwright_TimeoutError

from math import ceil

from app.core.models import Proxy, File

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

import urllib.parse as up
import pandas as pd
import json
import asyncio


user_data = {}

async def get_files(user_id: int, session: AsyncSession):
    stmt = select(File).where(File.user_id==user_id).order_by(File.date)
    result: Result = await session.execute(stmt)
    files = result.scalars().all()

    return files

def not_files(files):
    if files == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не загружен"
        )

def not_in_user_data(payload):
    if payload.get("sub") not in user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Невозможно посмотреть статус"
        )

def create(df_to_list):
    brands = []
    nums = []
    try:
        for df in df_to_list:
            brands.append((df_to_list.index(df), df[2]))
            nums.append((df_to_list.index(df), df[3]))
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Некорректный файл excel"
        )
    
    return brands, nums

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

async def main(brands, nums, user_id):
    global user_data
    if len(user_data[user_id]["proxies"]) > 0:
        proxy = user_data[user_id]["proxies"].pop(0) # в словарь
    else:
        proxy = ["0.0.0.0", "user", "pass"]
    for brand, num in zip(brands, nums):
        if all([event.is_set() for event in user_data[user_id]["events"]]):
            break   
        if proxy[0] not in user_data[user_id]["atms_proxy"]: # в словарь
            user_data[user_id]["atms_proxy"][proxy[0]] = 0 # в словарь

        if user_data[user_id]["atms_proxy"][proxy[0]] > 7: # в словарь
            if proxy not in user_data[user_id]["ban_list"]: # в словарь
                user_data[user_id]["ban_list"].append(proxy) # в словарь
            if proxy in user_data[user_id]["proxies"]: # в словарь
                user_data[user_id]["proxies"].remove(proxy) # в словарь
            if len(user_data[user_id]["ban_list"]) == user_data[user_id]["proxies_count"]: # в словарь
                raise HTTPException(
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    detail="У вас закончились прокси"
                )
                break
            if user_data[user_id]["proxies"] != []:
                proxy = user_data[user_id]["proxies"].pop(0)

        skip = False
        url = f"https://emex.ru/api/search/search?make={create_params_for_url(brand[1])}&detailNum={num[1]}&locationId=38760&showAll=true&longitude=37.8613&latitude=55.7434"
        async with async_playwright() as p:
            browser = await p.chromium.launch(proxy={"server": proxy[0], "username": proxy[1], "password": proxy[2]}, headless=True)
            # browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            try:
                await page.goto(url, timeout=3000)
            except:
                brands.append(brand)
                nums.append(num)
                
                if proxy[0] in user_data[user_id]["atms_proxy"]:
                    user_data[user_id]["atms_proxy"][proxy[0]] += 1
                if user_data[user_id]["atms_proxy"][proxy[0]] > 7:
                    if proxy not in user_data[user_id]["ban_list"]:
                        user_data[user_id]["ban_list"].append(proxy)
                    if proxy in user_data[user_id]["proxies"]:
                        user_data[user_id]["proxies"].remove(proxy)
                    if len(user_data[user_id]["ban_list"]) == user_data[user_id]["proxies_count"]:
                        raise HTTPException(
                            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail="У вас закончились прокси"
                        )
                        break
                    if user_data[user_id]["proxies"] != []:
                        proxy = user_data[user_id]["proxies"].pop(0)
                continue

            pre = await (await page.query_selector("pre")).text_content()
            response = dict(json.loads(pre))

            if "originals" not in response["searchResult"]:
                user_data[user_id]["all_data"].append([brand[1], num[1], 'ТОВАР', "НЕ", "ДОСТУПЕН"])
                #  if proxy[0] in atms_proxy:
                #     atms_proxy[proxy[0]] += 1
                continue

            originals = response["searchResult"]["originals"]
            if "analogs" in response["searchResult"]:
                analogs = response["searchResult"]["analogs"]

            goods = originals   
            goods = originals + analogs[:3]
            final_data_of_goods = []
            k = 0

            for good in goods:
                data_of_goods = []
                for number_of_goods in range(12):
                    if all([event.is_set() for event in user_data[user_id]["events"]]):
                        skip = True
                        await browser.close()
                        break   
                    k += 1
                    try:   
                        offer = good["offers"][number_of_goods]
                        
                        key_for_logo = offer["offerKey"]
                        delivery = offer["delivery"]["value"]
                        display_price = offer["displayPrice"]["value"]

                        data = offer["data"]

                        quantity = data["maxQuantity"]["value"]

                        try:
                            await page.goto(f"https://emex.ru/api/search/rating?offerKey={key_for_logo}", timeout=1500)
                        except:
                            await page.goto(f"https://emex.ru/api/search/rating?offerKey={key_for_logo}", timeout=1500)

                        pre_with_logo = await (await page.query_selector("pre")).text_content()

                        response_with_logo = dict(json.loads(pre_with_logo))

                        price_logo = response_with_logo["priceLogo"] 

                        data_of_goods.append([delivery, display_price, quantity, price_logo])
                    except IndexError:
                        break
                    except playwright_TimeoutError:
                        if proxy[0] in user_data[user_id]["atms_proxy"]:
                            user_data[user_id]["atms_proxy"][proxy[0]] += 1
                        brands.append(brand)
                        nums.append(num)
                        skip = True
                        if user_data[user_id]["atms_proxy"][proxy[0]] > 7:
                            if proxy not in user_data[user_id]["ban_list"]:
                                user_data[user_id]["ban_list"].append(proxy)
                            if proxy in user_data[user_id]["proxies"]:
                                user_data[user_id]["proxies"].remove(proxy)
                            if len(user_data[user_id]["ban_list"]) == user_data[user_id]["proxies_count"]:
                                raise HTTPException(
                                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                    detail="У вас закончились прокси"
                                )
                                break
                            if user_data[user_id]["proxies"] != []:
                                proxy = user_data[user_id]["proxies"].pop(0)
                        break
                if skip:
                    break

                sort_data_of_goods = quick_sort(data_of_goods, 0)
                if sort_data_of_goods == []:
                    skip = True
                else:
                    final_data_of_goods.append(min(sort_data_of_goods[:10], key=lambda x: x[1]))

            if not skip:
                # with open('app/api_v1/parser/data.txt', 'a', encoding="utf-8") as file:
                #     file.write(f"{k} | {threading.current_thread().name} | {brand} | {num} | {min(final_data_of_goods, key=lambda x: x[1])}\n")
                min_goods = min(final_data_of_goods, key=lambda x: x[1])

                user_data[user_id]["all_data"].append([brand[1], num[1], min_goods[3], min_goods[0], min_goods[1]])

        user_data[user_id]["total"] += k
        await browser.close() 

    user_data[user_id]["proxies"].append(proxy)

def run(brands, nums, user_id):
    asyncio.run(main(brands, nums, user_id))