from fastapi import WebSocket, APIRouter, Request, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from playwright.async_api import async_playwright, TimeoutError as playwright_TimeoutError

from threading import Event, Thread

from app.core.config import settings
from app.api_v1.users.crud import get_payload
from math import ceil

import time
import asyncio
import json
import pandas as pd


def create(df_to_list):
    brands = []
    nums = []
    for i in df_to_list:
        brands.append((df_to_list.index(i), i[2]))
        nums.append((df_to_list.index(i), i[3]))
    
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

user_data = {}
router = APIRouter(prefix="/parser", tags=["Parser"])

async def main(brands, nums, user_id):
    global user_data
    user_data[user_id]["proxy"] = user_data[user_id]["proxies"].pop(0) # в словарь

    for brand, num in zip(brands, nums):
        if all([event.is_set() for event in user_data[user_id]["events"]]):
            break   
        if user_data[user_id]["proxy"][0] not in user_data[user_id]["atms_proxy"]: # в словарь
            user_data[user_id]["atms_proxy"][user_data[user_id]["proxy"][0]] = 0 # в словарь

        if user_data[user_id]["atms_proxy"][user_data[user_id]["proxy"][0]] > 7: # в словарь
            if user_data[user_id]["proxy"] not in user_data[user_id]["ban_list"]: # в словарь
                user_data[user_id]["ban_list"].append(user_data[user_id]["proxy"]) # в словарь
            if user_data[user_id]["proxy"] in user_data[user_id]["proxies"]: # в словарь
                user_data[user_id]["proxies"].remove(user_data[user_id]["proxy"]) # в словарь
            if len(user_data[user_id]["ban_list"]) == user_data[user_id]["proxies_count"]: # в словарь
                print("У вас закончились прокси") 
                break
            if user_data[user_id]["proxies"] != []:
                user_data[user_id]["proxy"] = user_data[user_id]["proxies"].pop(0)

        skip = False
        url = f"https://emex.ru/api/search/search?make={create_params_for_url(brand[1])}&detailNum={num[1]}&locationId=38760&showAll=true&longitude=37.8613&latitude=55.7434"
        async with async_playwright() as p:
            browser = await p.chromium.launch(proxy={"server": user_data[user_id]["proxy"][0], "username": user_data[user_id]["proxy"][1], "password": user_data[user_id]["proxy"][2]}, headless=False)
            print({"server": user_data[user_id]["proxy"][0], "username": user_data[user_id]["proxy"][1], "password": user_data[user_id]["proxy"][2]})
            # browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            try:
                await page.goto(url, timeout=3000)
            except:
                brands.append(brand)
                nums.append(num)
                
                if user_data[user_id]["proxy"][0] in user_data[user_id]["atms_proxy"]:
                    user_data[user_id]["atms_proxy"][user_data[user_id]["proxy"][0]] += 1
                if user_data[user_id]["atms_proxy"][user_data[user_id]["proxy"][0]] > 7:
                    if user_data[user_id]["proxy"] not in user_data[user_id]["ban_list"]:
                        user_data[user_id]["ban_list"].append(user_data[user_id]["proxy"])
                    if user_data[user_id]["proxy"] in user_data[user_id]["proxies"]:
                        user_data[user_id]["proxies"].remove(user_data[user_id]["proxy"])
                    if len(user_data[user_id]["ban_list"]) == user_data[user_id]["proxies_count"]:
                        print("У вас закончились прокси")
                        break
                    if user_data[user_id]["proxies"] != []:
                        user_data[user_id]["proxy"] = user_data[user_id]["proxies"].pop(0)
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
                        if user_data[user_id]["proxy"][0] in user_data[user_id]["atms_proxy"]:
                            user_data[user_id]["atms_proxy"][user_data[user_id]["proxy"][0]] += 1
                        brands.append(brand)
                        nums.append(num)
                        skip = True
                        if user_data[user_id]["atms_proxy"][user_data[user_id]["proxy"][0]] > 7:
                            if user_data[user_id]["proxy"] not in user_data[user_id]["ban_list"]:
                                user_data[user_id]["ban_list"].append(user_data[user_id]["proxy"])
                            if user_data[user_id]["proxy"] in user_data[user_id]["proxies"]:
                                user_data[user_id]["proxies"].remove(user_data[user_id]["proxy"])
                            if len(user_data[user_id]["ban_list"]) == user_data[user_id]["proxies_count"]:
                                print("У вас закончились прокси")
                                break
                            if user_data[user_id]["proxies"] != []:
                                user_data[user_id]["proxy"] = user_data[user_id]["proxies"].pop(0)
                        break
                if skip:
                    break

                sort_data_of_goods = quick_sort(data_of_goods, 0)
                final_data_of_goods.append(min(sort_data_of_goods[:10], key=lambda x: x[1]))

            if not skip:
                # with open('app/api_v1/parser/data.txt', 'a', encoding="utf-8") as file:
                #     file.write(f"{k} | {threading.current_thread().name} | {brand} | {num} | {min(final_data_of_goods, key=lambda x: x[1])}\n")
                min_goods = min(final_data_of_goods, key=lambda x: x[1])

                user_data[user_id]["all_data"].append([brand[1], num[1], min_goods[3], min_goods[0], min_goods[1]])

        user_data[user_id]["total"] += k
        await browser.close() 

    user_data[user_id]["proxies"].append(user_data[user_id]["proxy"])

def run(brands, nums, user_id):
    asyncio.run(main(brands, nums, user_id))

count_of_thread = 4

templates = Jinja2Templates(directory=settings.templates.templates_path)

@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse(
        request=request, name="test.html"
    )

@router.get("/start/")
async def start_threadings(payload = Depends(get_payload)):
    proxies = [
        # ["http://46.8.16.194:1050", "LorNNF", "fr4B7cGdyS"],
        # ["http://194.156.123.115:1050", "LorNNF", "fr4B7cGdyS"],
        ["http://109.258.166.189:1050", "LorNNF", "fr4B7cGdyS"], #109.248.166.189:1050
        # ["http://91.188.244.80:1050", "LorNNF", "fr4B7cGdyS"],
        # ["http://193.58.168.161:1050", "LorNNF", "fr4B7cGdyS"],
        # ["http://46.8.22.63:1050", "LorNNF", "fr4B7cGdyS"],
        # ["http://46.8.10.206:1050", "2Q3n1o", "FjvCaesiwS"], #!!!
        # ["http://109.248.14.248:1050", "LorNNF", "fr4B7cGdyS"],
        # ["http://2.59.50.242:1050", "LorNNF", "fr4B7cGdyS"],
        # ["http://94.158.190.152:1050", "LorNNF", "fr4B7cGdyS"],
        # ["http://188.130.188.9:1050", "2Q3n1o", "FjvCaesiwS"], #!!!
    #     ["http://188.130.129.128:1050", "LorNNF", "fr4B7cGdyS"],
        ["http://31.40.203.252:1050", "LorNNF", "fr4B7cGdyS"],
        ["http://45.15.73.112:1050", "LorNNF", "fr4B7cGdyS"],
        ["http://46.8.157.208:1050", "LorNNF", "fr4B7cGdyS"],
    #     ["http://188.130.128.166:1050", "LorNNF", "fr4B7cGdyS"],
    ]

    global user_data
    
    user_data[payload.get("sub")] = {"proxies": proxies, "atms_proxy": {}, "ban_list": [], "total": 0, "proxies_count": len(proxies), "all_data": [],
                                    "threads": [None] * count_of_thread, "events": [Event() for _ in range(count_of_thread)]}
    df = pd.read_excel("app/api_v1/parser/file.xlsx")

    df = df.apply(lambda col: col.astype(object))
    df_to_list = df.values.tolist()
    brands, nums = create(df_to_list)
    user_data[payload.get("sub")]["len_brands"] = len(brands)

    brands_split = split_file_for_thr(count_of_thread, brands)
    nums_split = split_file_for_thr(count_of_thread, nums)
    messages = []

    # await main(brands_split[0], nums_split[0], payload.get("sub"))

    for index in range(count_of_thread):
        if user_data[payload.get("sub")]["threads"][index] is None or not user_data[payload.get("sub")]["threads"][index].is_alive():
            user_data[payload.get("sub")]["events"][index].clear()
            user_data[payload.get("sub")]["threads"][index] = Thread(target=run, args=(brands_split[index], nums_split[index], payload.get("sub")))
            user_data[payload.get("sub")]["threads"][index].start()
            messages.append("старт")
        else:
            messages.append("уже началось")

    return JSONResponse(content=messages)

@router.get("/stop/")
async def stop_threadings(payload=Depends(get_payload)):
    global user_data
    for index in range(count_of_thread):
        user_data[payload.get("sub")]["events"][index].set()
    return JSONResponse(content={"message": "все потоки прекращены"})

@router.get("/status_check/")
async def status_threadings(payload = Depends(get_payload)):
    global user_data

    return JSONResponse(content={"user_data": user_data[payload.get("sub")]["all_data"]})

@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket, payload=Depends(get_payload)):
    global user_data
    await websocket.accept()

    while True:
        if payload.get("sub") in user_data:
            len_ban = len(user_data[payload.get("sub")]["ban_list"])
            proxies = user_data[payload.get("sub")]["proxies_count"]
            len_all_data = len(user_data[payload.get("sub")]["all_data"])
            len_brands = user_data[payload.get("sub")]["len_brands"]
            await websocket.send_json({
                "ban_proxies": round(len_ban/proxies, 2)*100,
                "full": round(len_all_data/len_brands, 2)*100
            })
            await asyncio.sleep(2)
        else:
            await websocket.send_json({
                "message": "запустите парсер"
            })