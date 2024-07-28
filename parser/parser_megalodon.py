from playwright.async_api import async_playwright, TimeoutError as playwright_TimeoutError

import asyncio
import json
import time 
import random
import threading

import urllib.parse as up

from math import ceil


proxies = [
    ["http://194.156.97.212:1050 ", "LorNNF", "fr4B7cGdyS"],
    ["http://194.156.123.115:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://109.248.166.189:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://91.188.244.80:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://193.58.168.161:1050", "LorNNF", "fr4B7cGdyS"],
] *2

atms_proxy = {}
ban_list = []
total = 0

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

async def main(brands, nums):
    global proxies, atms_proxy, ban_list, total
    proxy = proxies.pop(0)

    if proxy[0] not in atms_proxy:
        atms_proxy[proxy[0]] = 0

    if atms_proxy[proxy[0]] > 15:
        ban_list.append(proxy)
        proxies.remove(proxy)

    for brand, num in zip(brands, nums):
        url = f"https://emex.ru/api/search/search?make={create_params_for_url(brand)}&detailNum={num}&locationId=38760&showAll=true&longitude=37.8613&latitude=55.7434"
        async with async_playwright() as p:
            browser = await p.chromium.launch(proxy={"server": proxy[0], "username": proxy[1], "password": proxy[2]}, headless=True)
            # browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            try:
                await page.goto(url, timeout=3000)
            except:
                print("url1")
                brands.append(brand)
                nums.append(num)
                
                atms_proxy[proxy[0]] += 1

                continue

            pre = await (await page.query_selector("pre")).text_content()
            response = dict(json.loads(pre))

            originals = response["searchResult"]["originals"]
            analogs = response["searchResult"]["analogs"][:3]

            goods = originals   
            # goods = originals + analogs
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
                        print("url2")
                        atms_proxy[proxy[0]] += 1
                        brands.append(brand)
                        nums.append(num)

                sort_data_of_goods = quick_sort(data_of_goods, 0)
                final_data_of_goods.append(min(sort_data_of_goods[:10], key=lambda x: x[1]))

            with open('parser/data.txt', 'a', encoding="utf-8") as file:
                file.write(f"{k} | {brand} | {num} | {min(final_data_of_goods, key=lambda x: x[1])}\n")
        total += k
        await browser.close() 

    proxies.append(proxy)

def run(brands, nums):
    asyncio.run(main(brands, nums))

start = time.perf_counter()

brands = ["Peugeot---Citroen", "Mahle---Knecht", "Peugeot---Citroen", "Peugeot---Citroen", "Peugeot---Citroen", "Peugeot---Citroen", "ГАЗ", "VAG", "Autocomponent"] * 20
nums = ["82026", "02943N0", "362312", "00004254A2", "00006426YN", "00008120T7", "6270000290", "016409399B", "01М21С9"] * 20

brands_split = split_file_for_thr(8, brands)
nums_split = split_file_for_thr(8, nums)

threadings = []
for i in range(len(brands_split)):
    thread = threading.Thread(target=run, args=(brands_split[i], nums_split[i]), name=f"thr-{i}")
    thread.start()
    threadings.append(thread)

for thread in threadings:
    thread.join()

with open('parser/data.txt', 'a', encoding="utf-8") as file:
    file.write(f"ВСЕГО: {total} строк\nБан лист: {ban_list}\nПопытки: {atms_proxy}\nСкорость: {total/(time.perf_counter() - start)} строк/секунд\n{time.perf_counter() - start} секунд")