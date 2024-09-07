from fastapi import HTTPException, status

import asyncio
import json
import time

from .depends import *

from playwright.async_api import async_playwright


user_data = {}

# {"threads": threads.copy(), "events": [Event() for _ in range(count_of_threadings)], 
# "proxies": proxies, "filter": filter, "excel_result": [], "status": "Парсер не запущен",
# "count_proxies": len(proxies), "ban_list": set()}
   

columns = ["Артикул", "Наименование", "Брэнд", "Артикул", "Кол-во", "Цена", "Партия", "НДС", "Лого", "Доставка", "Лучшая цена", "Количество"]

async def main(brands, user_id):   
    global user_data, columns

    DEEP_FILTER = user_data[user_id]["filter"].deep_filter
    DEEP_ANALOG = user_data[user_id]["filter"].deep_analog
    ANALOG = user_data[user_id]["filter"].analog
    IS_BIGGER = user_data[user_id]["filter"].is_bigger #True - больше False - меньше None - не указано
    DATE = user_data[user_id]["filter"].date
    LOGO = user_data[user_id]["filter"].logo #HXAW - пример лого None - Без лого

    if LOGO and "Цена с лого" not in columns:
        columns.append("Цена с лого")

    if user_data[user_id]["proxies"] != []:
        proxy = user_data[user_id]["proxies"].pop(0)
        proxy = [proxy.ip_with_port, proxy.login, proxy.password]
    else:
        proxy = ["http://test:8888", "user1", "pass1"]
    for brand in brands:
        if all([ev.is_set() for ev in user_data[user_id]["events"]]):
            break

        if user_data[user_id]["count_proxies"] == len(user_data[user_id]["ban_list"]):
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Закочнились прокси"
            )
            break
        url = f"https://emex.ru/api/search/search?make={create_params_for_url(brand[2])}&detailNum={brand[0]}&locationId=38760&showAll=true&longitude=37.8613&latitude=55.7434"
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True, proxy={"server": proxy[0], "username": proxy[1], "password": proxy[2]})
                page = await browser.new_page()

                try:
                    await page.goto(url, timeout=4444)
                except:
                    await page.goto(url, timeout=4444)

                pre = await (await page.query_selector("pre")).text_content()
                response = dict(json.loads(pre))
                originals = []
                if IS_BIGGER is None:
                    if "originals" in response["searchResult"]:
                        originals += [[goods["offerKey"], int(str(goods["delivery"]["value"]).replace("Завтра", "1")), goods["displayPrice"]["value"], goods["data"]["maxQuantity"]["value"]] for orig in response["searchResult"]["originals"] for goods in orig["offers"]]
                    else:
                        result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], "Пусто", "Пусто", "Пусто", "Товар не подходит под фильтр/Товара нет в наличие"]
                        if LOGO:
                            result.append("Товара нет в наличие")
                        # continue

                    if "replacements" in response["searchResult"]:
                        originals += [[goods["offerKey"], int(str(goods["delivery"]["value"]).replace("Завтра", "1")), goods["displayPrice"]["value"], goods["data"]["maxQuantity"]["value"]] for repl in response["searchResult"]["replacements"] for goods in repl["offers"]]

                    if ANALOG and "analogs" in response["searchResult"]:
                        originals += [[goods["offerKey"], int(str(goods["delivery"]["value"]).replace("Завтра", "1")), goods["displayPrice"]["value"], goods["data"]["maxQuantity"]["value"]] for anal in response["searchResult"]["analogs"][:DEEP_ANALOG] for goods in anal["offers"]]
                else:
                    if "originals" in response["searchResult"]:
                        if IS_BIGGER:
                            originals += [[goods["offerKey"], int(str(goods["delivery"]["value"]).replace("Завтра", "1")), goods["displayPrice"]["value"], goods["data"]["maxQuantity"]["value"]] if int(str(goods["delivery"]["value"]).replace("Завтра", "1")) >= DATE else False for orig in response["searchResult"]["originals"] for goods in orig["offers"]]
                        else:
                            originals += [[goods["offerKey"], int(str(goods["delivery"]["value"]).replace("Завтра", "1")), goods["displayPrice"]["value"], goods["data"]["maxQuantity"]["value"]] if int(str(goods["delivery"]["value"]).replace("Завтра", "1")) <= DATE else False for orig in response["searchResult"]["originals"] for goods in orig["offers"]]
                    else:
                        result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], "Пусто", "Пусто", "Пусто", "Товар не подходит под фильтр/Товара нет в наличие"]
                        if LOGO:
                            result.append("Товара нет в наличие")
                        # continue

                    if "replacements" in response["searchResult"]:
                        if IS_BIGGER:
                            originals += [[goods["offerKey"], int(str(goods["delivery"]["value"]).replace("Завтра", "1")), goods["displayPrice"]["value"], goods["data"]["maxQuantity"]["value"]] if int(str(goods["delivery"]["value"]).replace("Завтра", "1")) >= DATE else False for orig in response["searchResult"]["replacements"] for goods in orig["offers"]]
                        else:
                            originals += [[goods["offerKey"], int(str(goods["delivery"]["value"]).replace("Завтра", "1")), goods["displayPrice"]["value"], goods["data"]["maxQuantity"]["value"]] if int(str(goods["delivery"]["value"]).replace("Завтра", "1")) <= DATE else False for orig in response["searchResult"]["replacements"] for goods in orig["offers"]]

                    if ANALOG and "analogs" in response["searchResult"]:
                        if IS_BIGGER:
                            originals += [[goods["offerKey"], int(str(goods["delivery"]["value"]).replace("Завтра", "1")), goods["displayPrice"]["value"], goods["data"]["maxQuantity"]["value"]] if int(str(goods["delivery"]["value"]).replace("Завтра", "1")) >= DATE else False for orig in response["searchResult"]["analogs"][:DEEP_ANALOG] for goods in orig["offers"]]
                        else:
                            originals += [[goods["offerKey"], int(str(goods["delivery"]["value"]).replace("Завтра", "1")), goods["displayPrice"]["value"], goods["data"]["maxQuantity"]["value"]] if int(str(goods["delivery"]["value"]).replace("Завтра", "1")) <= DATE else False for orig in response["searchResult"]["analogs"][:DEEP_ANALOG] for goods in orig["offers"]]
                    
                    originals = [data for data in originals if data]

                if originals == []:
                    result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], "Пусто", "Пусто", "Пусто", "Товар не подходит под фильтр/Товара нет в наличие"]
                    if LOGO:
                        result.append("Пусто")
                    user_data[user_id]["excel_result"].append(result)
                else:

                    sorted_data_by_date = quick_sort(originals, 1)
                    # cut_data_by_date = sorted_data_by_date[:len(sorted_data_by_date)//2+1]
                    cut_data_by_date = sorted_data_by_date[:DEEP_FILTER]

                    # sorted_data_by_availability = quick_sort(cut_data_by_date, 3)
                    # cut_data_by_availability = sorted_data_by_availability[-DEEP_FILTER:]

                    # best_data = min(cut_data_by_availability, key=lambda x: x[2])
                    sorted_by_price = quick_sort(cut_data_by_date, 2)
                    best_data = sorted_by_price[0]

                    try:
                        await page.goto(f"https://emex.ru/api/search/rating?offerKey={best_data[0]}", timeout=4444)
                    except:
                        await page.goto(f"https://emex.ru/api/search/rating?offerKey={best_data[0]}", timeout=4444)

                    pre_with_logo = await (await page.query_selector("pre")).text_content()
                    response_with_logo = dict(json.loads(pre_with_logo))
                    price_logo = response_with_logo["priceLogo"] 

                    # result = [price_logo, *best_data[1:]]
                    result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], price_logo, *best_data[1:]]
                    atms = 0
                    if LOGO:
                        best_data = None
                        sorted_by_price = quick_sort(originals, 2)[:20]
                        for data in sorted_by_price:
                            try:
                                if atms == 25:
                                    raise Exception
                                await page.goto(f"https://emex.ru/api/search/rating?offerKey={data[0]}", timeout=4444)
                            except:
                                atms += 1
                                sorted_by_price.append(data)
                                continue

                            pre_with_logo = await (await page.query_selector("pre")).text_content()
                            response_with_logo = dict(json.loads(pre_with_logo))
                            price_logo = response_with_logo["priceLogo"] 

                            data[0] = price_logo
                            if price_logo == LOGO:
                                best_data = data
                                break

                        if best_data:
                            result.append(best_data[2])
                        else:
                            result.append("Нет такого лого среди оригиналов")
                    user_data[user_id]["excel_result"].append(result)
            except Exception as e:
                brands.append(brand)
                if proxy != ["http://test:8888", "user1", "pass1"]:
                    user_data[user_id]["ban_list"].add("@".join(proxy))
                if user_data[user_id]["proxies"] != []:
                    proxy = user_data[user_id]["proxies"].pop(0)
                    try:
                        proxy = [proxy.ip_with_port, proxy.login, proxy.password]
                    except:
                        proxy = [proxy[0], proxy[1], proxy[2]]
                else:
                    proxy = ["http://test:8888", "user1", "pass1"]
    user_data[user_id]["proxies"].append(proxy)
        
def run(brands, user_id):
    asyncio.run(main(brands, user_id))