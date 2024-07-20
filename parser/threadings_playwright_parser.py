from playwright.async_api import async_playwright, TimeoutError as playwright_TimeoutError

from math import ceil

import asyncio
import json
import time 
import random
import threading
import requests


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

def quick_sort(arr, index):
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

async def main(brands, nums, proxies):
    '''
    Парсер
    brands - бренды, которые указываются в url make=
    num - артикулы, который указываются в url detailNum=
    proxies - список с прокси, который выбираются случайно
    
    Берем первые 30 товаров, сортируем их по дате доставки и записываем минимальную цену из 10 отсортированных цен по дате
    '''
    global ag_brand, ag_num
    k = 0
    for brand, num in zip(brands, nums):
        unsort_list_for_goods = []
        
        proxy = random.choice(proxies)

        url = f"https://emex.ru/api/search/search?make={brand}&detailNum={num}&locationId=38760&showAll=true&longitude=37.8613&latitude=55.7434"
        async with async_playwright() as p:
            browser = await p.chromium.launch(proxy={'server': proxy[0], 'username': proxy[1], 'password': proxy[2]}, headless=False)
            page = await browser.new_page()
            try:
                print('1)')
                await page.goto(url, timeout=2222)
            except:
                await page.reload()
            await page.mouse.wheel(0, 15000)

            try:
                await page.wait_for_selector('pre', timeout=2222)
                pre = await (await page.query_selector("pre")).text_content()
                response_data = dict(json.loads(pre))
                
                for i in range(30):
                    try:
                        data = response_data["searchResult"]["originals"][0]["offers"][i]
                        quantity = data["data"]["maxQuantity"]["value"]
                        date = data["delivery"]["value"]
                        price = data["displayPrice"]["value"]

                        offer_key_for_logo = data["data"]["offerKey"]
                        try:
                            await page.goto(f'https://emex.ru/api/search/rating?offerKey={offer_key_for_logo}', timeout=2222)
                        except:
                            print('2)')
                            await page.reload()

                        await page.wait_for_selector('pre', timeout=2222)
                        pre_logo = await (await page.query_selector("pre")).text_content()
                        logo_data = dict(json.loads(pre_logo))

                        logo = logo_data["priceLogo"]

                        unsort_list_for_goods.append([quantity, date, price, logo])
                    except IndexError:
                        break
                    except playwright_TimeoutError:
                        print(i, "error1", url)
                        ag_brand.append(brand)
                        ag_num.append(num)
                    except:
                        continue
                k += 1
            except playwright_TimeoutError:
                print("error2", url)
                again.append((brands, num))

            if unsort_list_for_goods != []:
                min_price_and_data = min(quick_sort(unsort_list_for_goods[:10], 1), key=lambda x: x[2]) 
                with open('parser/data.txt', 'a', encoding="UTF-8") as file:
                    file.write(f"{brand} {num} | Количество товара: {min_price_and_data[0]} Дата: {min_price_and_data[1]} Цена: {min_price_and_data[2]} Лого: {min_price_and_data[3]}\n")

            await browser.close()
    print("_____", k)

def run(brands, nums, proxies):
    asyncio.run(main(brands, nums, proxies))

if __name__ == "__main__":
    start = time.perf_counter()

    ag_brand = []
    ag_num = []

    proxies = [
        ["http://194.35.113.239:1050", "2Q3n1o", "FjvCaesiwS"],
        ["http://188.130.210.107:1050", "2Q3n1o", "FjvCaesiwS"],
        ["http://109.248.139.54:1050", "2Q3n1o", "FjvCaesiwS"],
        ["http://185.181.245.74:1050", "2Q3n1o", "FjvCaesiwS"],

        ["http://109.248.167.161:1050", "2Q3n1o", "FjvCaesiwS"],
        ["http://188.130.219.173:1050", "2Q3n1o", "FjvCaesiwS"],
        # ["http://45.81.136.39:1050", "2Q3n1o", "FjvCaesiwS"],
        ["http://95.182.124.119:1050", "2Q3n1o", "FjvCaesiwS"],
    ]

    brands = ["Peugeot+%2F+Citroen", "Mahle---Knecht", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "%D0%93%D0%90%D0%97", "VAG", "Autocomponent"] * 15
    nums = ["82026", "02943N0", "362312", "00004254A2", "00006426YN", "00008120T7", "6270000290", "016409399B", "01М21С9"] * 15
    brands_split = split_file_for_thr(4, brands)
    nums_split = split_file_for_thr(4, nums)

    threadings = []
    for i in range(len(brands_split)):
        thread = threading.Thread(target=run, args=(brands_split[i], nums_split[i], proxies), name=f"thr-{i}")
        thread.start()
        threadings.append(thread)

    for thread in threadings:
        thread.join()

    asyncio.run(main(ag_brand, ag_num, proxies))

    print(time.perf_counter() - start)