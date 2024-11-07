from fastapi import HTTPException, status

import asyncio
import json
import time
import random
import requests
import aiohttp
import threading
import os
import aiofiles

from app.core.config import settings
from .depends import *

from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

user_data = {}

USERAGENTS = [
    "Mediapartners-Google",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.3.136 Yowser/2.5 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 YaBrowser/21.3.3.230 Yowser/2.5 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/62.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.1; rv:84.0) Gecko/20100101 Firefox/84.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36 Maxthon/5.3.8.2000",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 YaBrowser/20.12.2.105 Yowser/2.5 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 YaBrowser/21.8.1.468 Yowser/2.5 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
]

user_locks = {}

async def rezerv_copy(filepath: str, data: dict):
    async with aiofiles.open(filepath, mode='a', encoding='utf-8') as f:
        json_data = json.dumps(data, ensure_ascii=False, indent=4)
        await f.write(json_data)

async def main(user_id, using_proxy):
    global user_data, user_locks
    user_locks[user_id] = threading.Lock()

    DEEP_FILTER = user_data[user_id]["filter"].deep_filter
    DEEP_ANALOG = user_data[user_id]["filter"].deep_analog
    ANALOG = user_data[user_id]["filter"].analog
    REPLACEMENT = user_data[user_id]["filter"].replacement
    IS_BIGGER = user_data[user_id]["filter"].is_bigger 
    DATE = user_data[user_id]["filter"].date
    LOGO = user_data[user_id]["filter"].logo 
    PICKUP_POINT = user_data[user_id]["filter"].pickup_point
    browser = None
    user_data[user_id]["all_break"] = False
    # user_data[user_id]["columns"] = ["Артикул", "Наименование", "Брэнд", "Артикул", "Кол-во", "Цена", "Партия", "НДС", "Лого", "Доставка", "Лучшая цена", "Количество",]
    user_data[user_id]["columns"] = ["Код товара", "Артикул", "Наименование", "Брэнд", "Артикул", "Кол-во", "Цена", "Цена ABCP", "Партия", "Лого", "Доставка", "Лучшая цена", "Количество",]

    if LOGO and "Цена с лого" not in user_data[user_id]["columns"]:
        user_data[user_id]["columns"].append("Цена с лого")

    while user_data[user_id]["status"] == "PARSER_RUNNING":
        headers = {'User-Agent': random.choice(USERAGENTS)}

        for stop in user_data[user_id]["stop"]:
            if stop:
                print("Остановка парсера началась!")
                user_data[user_id]["status"] = "Парсер не запущен"
                user_data[user_id]["excel_result"] = []
                user_data[user_id]["counter_parsered"] = 0
                user_data[user_id]["brands"] = []
                user_data[user_id]["ban_list"] = []
                return

        if user_data[user_id]["all_break"]:
            user_data[user_id]["status"] = "Парсер не запущен"
            return
        
        if len(user_data[user_id]["brands"]) == 0 or all([ev.is_set() for ev in user_data[user_id]["events"]]) or user_data[user_id]["all_break"]:
            user_data[user_id]["status"] = "Парсер не запущен"
            return

        with user_locks[user_id]:
            brand = user_data[user_id]["brands"].pop(0)
        if user_locks[user_id].locked():
            print(f"1. Поток {threading.current_thread().name} ожидает разблокировки")
        else:
            print(f"1. Поток {threading.current_thread().name} не блокирован")

        url = f"https://emex.ru/api/search/search?make={create_params_for_url(brand[3])}&detailNum={brand[1]}&locationId={PICKUP_POINT}&showAll=true&longitude=37.8613&latitude=55.7434"
        
        try:
            for_log = f"-=-=-=-=-=-=-={threading.current_thread().name}=-=-=-=-=-=-=-"
            print(for_log)
            if user_data[user_id]["count_brands"] == 0:
                user_data[user_id]["count_brands"] = 1
            print(int(user_data[user_id]["counter_parsered"] / user_data[user_id]["count_brands"] * 100))
            print(user_data[user_id]["status"])
            print("URL сейчас:", url)
            print("Данных спаршено:", user_data[user_id]["counter_parsered"], "данных всего:", user_data[user_id]["count_brands"])
            print("Обновление списка (длина):", len(user_data[user_id]["brands"]))
            print("Потоки", threading.enumerate())
            try:
                print(*[f"""{i} | {user_data[user_id]["threads"][i]}: {user_data[user_id]["threads"][i].is_alive()}""" for i in range(len(user_data[user_id]["threads"])) if user_data[user_id]["threads"][i] != None]) #4: {user_data[user_id]["threads"][4].is_alive()} 5: {user_data[user_id]["threads"][5].is_alive()}""")
            except Exception as e:
                print("Ошибка в alive модуле", e)
            print(f"-="*(len(for_log)//2))

            if using_proxy == "MANGO":
                proxies = os.getenv("MANGOPROXY")
            elif using_proxy == "BRIGHTDATA":
                proxies = os.getenv("BRIGHTDATAPROXY")
                
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, proxy=proxies, timeout=3, headers=headers) as resp:
                        response = await resp.json()
            except Exception as e:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, proxy=proxies, timeout=3, headers=headers) as resp:
                        response = await resp.json()
            originals = []

            if IS_BIGGER is None:
                if "originals" in response["searchResult"]:
                    originals += [
                        [
                            goods["offerKey"],
                            int(
                                str(goods["delivery"]["value"]).replace(
                                    "Завтра", "1"
                                )
                            ),
                            goods["displayPrice"]["value"],
                            goods["data"]["maxQuantity"]["value"],
                        ]
                        for orig in response["searchResult"]["originals"]
                        for goods in orig["offers"]
                    ]
                else:
                    result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], brand[8], 0, 0, 0, 0,]
                    if LOGO:
                        result.append(0)
                if REPLACEMENT and "replacements" in response["searchResult"]:
                    originals += [
                        [
                            goods["offerKey"],
                            int(
                                str(goods["delivery"]["value"]).replace(
                                    "Завтра", "1"
                                )
                            ),
                            goods["displayPrice"]["value"],
                            goods["data"]["maxQuantity"]["value"],
                        ]
                        for repl in response["searchResult"]["replacements"]
                        for goods in repl["offers"]
                    ]
                
                if ANALOG and "analogs" in response["searchResult"]:
                    originals += [
                        [
                            goods["offerKey"],
                            int(
                                str(goods["delivery"]["value"]).replace(
                                    "Завтра", "1"
                                )
                            ),
                            goods["displayPrice"]["value"],
                            goods["data"]["maxQuantity"]["value"],
                        ]
                        for anal in response["searchResult"]["analogs"][
                            :DEEP_ANALOG
                        ]
                        for goods in anal["offers"]
                    ]
            else:
                if "originals" in response["searchResult"]:
                    if IS_BIGGER:
                        originals += [
                            (
                                [
                                    goods["offerKey"],
                                    int(
                                        str(goods["delivery"]["value"]).replace(
                                            "Завтра", "1"
                                        )
                                    ),
                                    goods["displayPrice"]["value"],
                                    goods["data"]["maxQuantity"]["value"],
                                ]
                                if int(
                                    str(goods["delivery"]["value"]).replace(
                                        "Завтра", "1"
                                    )
                                )
                                >= DATE
                                else False
                            )
                            for orig in response["searchResult"]["originals"]
                            for goods in orig["offers"]
                        ]
                    else:
                        originals += [
                            (
                                [
                                    goods["offerKey"],
                                    int(
                                        str(goods["delivery"]["value"]).replace(
                                            "Завтра", "1"
                                        )
                                    ),
                                    goods["displayPrice"]["value"],
                                    goods["data"]["maxQuantity"]["value"],
                                ]
                                if int(
                                    str(goods["delivery"]["value"]).replace(
                                        "Завтра", "1"
                                    )
                                )
                                <= DATE
                                else False
                            )
                            for orig in response["searchResult"]["originals"]
                            for goods in orig["offers"]
                        ]
                else:
                    result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], brand[8], 0, 0, 0, 0,]
                    if LOGO:
                        result.append(0)

                if REPLACEMENT and "replacements" in response["searchResult"]:
                    if IS_BIGGER:
                        originals += [
                            (
                                [
                                    goods["offerKey"],
                                    int(
                                        str(goods["delivery"]["value"]).replace(
                                            "Завтра", "1"
                                        )
                                    ),
                                    goods["displayPrice"]["value"],
                                    goods["data"]["maxQuantity"]["value"],
                                ]
                                if int(
                                    str(goods["delivery"]["value"]).replace(
                                        "Завтра", "1"
                                    )
                                )
                                >= DATE
                                else False
                            )
                            for orig in response["searchResult"]["replacements"]
                            for goods in orig["offers"]
                        ]
                    else:
                        originals += [
                            (
                                [
                                    goods["offerKey"],
                                    int(
                                        str(goods["delivery"]["value"]).replace(
                                            "Завтра", "1"
                                        )
                                    ),
                                    goods["displayPrice"]["value"],
                                    goods["data"]["maxQuantity"]["value"],
                                ]
                                if int(
                                    str(goods["delivery"]["value"]).replace(
                                        "Завтра", "1"
                                    )
                                )
                                <= DATE
                                else False
                            )
                            for orig in response["searchResult"]["replacements"]
                            for goods in orig["offers"]
                        ]
                
                if ANALOG and "analogs" in response["searchResult"]:
                    if IS_BIGGER:
                        originals += [
                            (
                                [
                                    goods["offerKey"],
                                    int(
                                        str(goods["delivery"]["value"]).replace(
                                            "Завтра", "1"
                                        )
                                    ),
                                    goods["displayPrice"]["value"],
                                    goods["data"]["maxQuantity"]["value"],
                                ]
                                if int(
                                    str(goods["delivery"]["value"]).replace(
                                        "Завтра", "1"
                                    )
                                )
                                >= DATE
                                else False
                            )
                            for orig in response["searchResult"]["analogs"][
                                :DEEP_ANALOG
                            ]
                            for goods in orig["offers"]
                        ]
                    else:
                        originals += [
                            (
                                [
                                    goods["offerKey"],
                                    int(
                                        str(goods["delivery"]["value"]).replace(
                                            "Завтра", "1"
                                        )
                                    ),
                                    goods["displayPrice"]["value"],
                                    goods["data"]["maxQuantity"]["value"],
                                ]
                                if int(
                                    str(goods["delivery"]["value"]).replace(
                                        "Завтра", "1"
                                    )
                                )
                                <= DATE
                                else False
                            )
                            for orig in response["searchResult"]["analogs"][
                                :DEEP_ANALOG
                            ]
                            for goods in orig["offers"]
                        ]

                originals = [data for data in originals if data]
            if originals == []:
                result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], brand[8], 0, 0, 0, 0,]
                if LOGO:
                    result.append(0)
                with user_locks[user_id]:
                    user_data[user_id]["excel_result"].append(result)
                    saving_to_json = {
                        "good_code": result[0],
                        "article": result[1],
                        "name": result[2],
                        "brand": result[3],
                        "article1": result[4],
                        "quantity": result[5],
                        "price": result[6],
                        "abcpprice": result[7],
                        "batch": result[8],
                        "logo": result[9],
                        "delivery_time": result[10],
                        "best_price": result[11],
                        "quantity1": result[12]
                    }
                    if len(result) > 13: saving_to_json["new_price"] = result[13]
                    await rezerv_copy(os.path.join(settings.upload.path_for_upload, f"{user_id}_parsing.json"), saving_to_json)
                    user_data[user_id]["counter_parsered"] += 1
                if user_locks[user_id].locked():
                    print(f"2. Поток {threading.current_thread().name} ожидает разблокировки")
                else:
                    print(f"2. Поток {threading.current_thread().name} не блокирован")
            
            else:
                sorted_data_by_date = quick_sort(originals, 1)
                # cut_data_by_date = sorted_data_by_date[:len(sorted_data_by_date)//2+1]
                cut_data_by_date = sorted_data_by_date[:DEEP_FILTER]

                # sorted_data_by_availability = quick_sort(cut_data_by_date, 3)
                # cut_data_by_availability = sorted_data_by_availability[-DEEP_FILTER:]

                # best_data = min(cut_data_by_availability, key=lambda x: x[2])
                sorted_by_price = quick_sort(cut_data_by_date, 2)
                best_data = sorted_by_price[0]
                for idx in range(len(best_data)):
                    try:
                        best_data[idx] = int(best_data[idx])
                    except:
                        pass

                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://emex.ru/api/search/rating?offerKey={best_data[0]}", timeout=3, proxy=proxies, headers=headers) as resp:
                            response_with_logo = await resp.json()
                except:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://emex.ru/api/search/rating?offerKey={best_data[0]}", timeout=3, proxy=proxies, headers=headers) as resp:
                            response_with_logo = await resp.json()
                await asyncio.sleep(0.2)    
                
                price_logo = response_with_logo["priceLogo"]

                result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], brand[8], price_logo, *best_data[1:],]
                if LOGO:
                    best_data = None
                    sorted_by_price = quick_sort(originals, 2)[:20]
                    for data in sorted_by_price:
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(f"https://emex.ru/api/search/rating?offerKey={data[0]}", timeout=4, proxy=proxies, headers=headers) as resp:
                                    response_with_logo = await resp.json()
                        except:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(f"https://emex.ru/api/search/rating?offerKey={data[0]}", timeout=5, proxy=proxies, headers=headers) as resp:
                                    response_with_logo = await resp.json()
                        price_logo = response_with_logo["priceLogo"]

                        data[0] = price_logo
                        if price_logo == LOGO:
                            best_data = data
                            break
                    if best_data:
                        result.append(int(best_data[2]))
                    else:
                        result.append(0)
                with user_locks[user_id]:
                    user_data[user_id]["excel_result"].append(result)
                    saving_to_json = {
                        "good_code": result[0],
                        "article": result[1],
                        "name": result[2],
                        "brand": result[3],
                        "article1": result[4],
                        "quantity": result[5],
                        "price": result[6],
                        "abcpprice": result[7],
                        "batch": result[8],
                        "logo": result[9],
                        "delivery_time": result[10],
                        "best_price": result[11],
                        "quantity1": result[12]
                    }
                    if len(result) > 13: saving_to_json["new_price"] = result[13]
                    await rezerv_copy(os.path.join(settings.upload.path_for_upload, f"{user_id}_parsing.json"), saving_to_json)
                    user_data[user_id]["counter_parsered"] += 1
                if user_locks[user_id].locked():
                    print(f"3. Поток {threading.current_thread().name} ожидает разблокировки")
                else:
                    print(f"3. Поток {threading.current_thread().name} не блокирован")
        except Exception as e:
            with user_locks[user_id]:
                user_data[user_id]["brands"].append(brand)
            msg = "message='Proxy Authentication Required'"
            if msg in repr(e):
                raise ProxyException("Proxy Authentication Required")

            print("-="*20)
            print("Общее исключение\nОшибка:", e, brand)
            print("-="*20)
            if user_locks[user_id].locked():
                print(f"4. Поток {threading.current_thread().name} ожидает разблокировки")
            else:
                print(f"4. Поток {threading.current_thread().name} не блокирован")
        except ProxyException as e:
            user_data[user_id]["status"] = "ALL_PROXIES_BANNED"
            user_data[user_id]["count_brands"] = user_data[user_id]["counter_parsered"]
            print("Трафик кончился")
            for index in range(count_of_threadings):
                user_data[user_id]["events"][index].set()
                user_data[user_id]["stop"][index] = True
            break

def run(user_id, using_proxy):
    asyncio.run(main(user_id, using_proxy))