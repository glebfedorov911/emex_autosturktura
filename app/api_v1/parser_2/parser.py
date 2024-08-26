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
   

columns = ["Артикул", "Номер товара", "Лого", "Доставка", "Лучшая цена", "Количество товара"]

async def main(brands, nums, user_id):   
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
    for brand, num in zip(brands, nums):
        if all([ev.is_set() for ev in user_data[user_id]["events"]]):
            break

        if user_data[user_id]["count_proxies"] == len(user_data[user_id]["ban_list"]):
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Закочнились прокси"
            )
            break
        url = f"https://emex.ru/api/search/search?make={create_params_for_url(brand[1])}&detailNum={num[1]}&locationId=38760&showAll=true&longitude=37.8613&latitude=55.7434"
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True, proxy={"server": proxy[0], "username": proxy[1], "password": proxy[2]})
                page = await browser.new_page()

                try:
                    await page.goto(url, timeout=2222)
                except:
                    await page.goto(url, timeout=2222)

                pre = await (await page.query_selector("pre")).text_content()
                response = dict(json.loads(pre))
                originals = []

                if IS_BIGGER is None:
                    if "originals" in response["searchResult"]:
                        originals += [[goods["offerKey"], int(str(goods["delivery"]["value"]).replace("Завтра", "1")), goods["displayPrice"]["value"], goods["data"]["maxQuantity"]["value"]] for orig in response["searchResult"]["originals"] for goods in orig["offers"]]
                    else:
                        result = [brand[1], num[1], "Пусто", "Пусто", "Пусто", "Пусто"]
                        if LOGO:
                            result.append("Товара нет в наличие")
                        continue

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
                        result = [brand[1], num[1], "Пусто", "Пусто", "Пусто", "Пусто"]
                        if LOGO:
                            result.append("Товара нет в наличие")
                        continue

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

                sorted_data_by_date = quick_sort(originals, 1)
                cut_data_by_date = sorted_data_by_date[:len(sorted_data_by_date)//2+1]

                sorted_data_by_availability = quick_sort(cut_data_by_date, 3)
                cut_data_by_availability = sorted_data_by_availability[-DEEP_FILTER:]

                best_data = min(cut_data_by_availability, key=lambda x: x[2])

                try:
                    await page.goto(f"https://emex.ru/api/search/rating?offerKey={best_data[0]}", timeout=2222)
                except:
                    await page.goto(f"https://emex.ru/api/search/rating?offerKey={best_data[0]}", timeout=2222)

                pre_with_logo = await (await page.query_selector("pre")).text_content()
                response_with_logo = dict(json.loads(pre_with_logo))
                price_logo = response_with_logo["priceLogo"] 

                # result = [price_logo, *best_data[1:]]
                result = [brand[1], num[1], price_logo, *best_data[1:]]
                
                if LOGO:
                    best_data = None
                    sorted_by_price = quick_sort(originals, 2)[:20]
                    for data in sorted_by_price:
                        try:
                            await page.goto(f"https://emex.ru/api/search/rating?offerKey={data[0]}", timeout=2222)
                        except:
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
                # if result not in user_data[user_id]["excel_result"]:
                user_data[user_id]["excel_result"].append(result)
                del result
                await browser.close()
            except Exception as e:
                print(e)
                brands.append(brand)
                nums.append(num)
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
                await browser.close()
    user_data[user_id]["proxies"].append(proxy)
        
def run(brands, nums, user_id):
    asyncio.run(main(brands, nums, user_id))