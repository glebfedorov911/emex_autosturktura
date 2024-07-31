from utils import *

import asyncio
import json
import time 
import random
import threading
import pandas as pd


atms_proxy = {}
ban_list = []
total = 0
proxies_count = len(proxies)
all_data = []

user_data = {}


async def main(brands, nums):
    global proxies, atms_proxy, ban_list, total, proxies_count, all_data, user_data
    proxy = proxies.pop(0)

    for brand, num in zip(brands, nums):
        if proxy[0] not in atms_proxy:
            atms_proxy[proxy[0]] = 0

        if atms_proxy[proxy[0]] > 7:
            if proxy not in ban_list:
                ban_list.append(proxy)
            if proxy in proxies:
                proxies.remove(proxy)
            if len(ban_list) == proxies_count:
                print("У вас закончились прокси")
                break
            if proxies != []:
                proxy = proxies.pop(0)

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
                
                if proxy[0] in atms_proxy:
                    atms_proxy[proxy[0]] += 1
                if atms_proxy[proxy[0]] > 7:
                    if proxy not in ban_list:
                        ban_list.append(proxy)
                    if proxy in proxies:
                        proxies.remove(proxy)
                    if len(ban_list) == proxies_count:
                        print("У вас закончились прокси")
                        break
                    if proxies != []:
                        proxy = proxies.pop(0)
                continue

            pre = await (await page.query_selector("pre")).text_content()
            response = dict(json.loads(pre))

            if "originals" not in response["searchResult"]:
                all_data.append([brand[1], num[1], 'ТОВАР', "НЕ", "ДОСТУПЕН"])
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
                        if proxy[0] in atms_proxy:
                            atms_proxy[proxy[0]] += 1
                        brands.append(brand)
                        nums.append(num)
                        skip = True
                        if atms_proxy[proxy[0]] > 7:
                            if proxy not in ban_list:
                                ban_list.append(proxy)
                            if proxy in proxies:
                                proxies.remove(proxy)
                            if len(ban_list) == proxies_count:
                                print("У вас закончились прокси")
                                break
                            if proxies != []:
                                proxy = proxies.pop(0)
                        break
                if skip:
                    break

                sort_data_of_goods = quick_sort(data_of_goods, 0)
                final_data_of_goods.append(min(sort_data_of_goods[:10], key=lambda x: x[1]))

            if not skip:
                # with open('app/api_v1/parser/data.txt', 'a', encoding="utf-8") as file:
                #     file.write(f"{k} | {threading.current_thread().name} | {brand} | {num} | {min(final_data_of_goods, key=lambda x: x[1])}\n")
                min_goods = min(final_data_of_goods, key=lambda x: x[1])

                all_data.append([brand[1], num[1], min_goods[3], min_goods[0], min_goods[1]])

        total += k
        await browser.close() 

    proxies.append(proxy)