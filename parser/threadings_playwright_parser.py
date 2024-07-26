from playwright.async_api import async_playwright, TimeoutError as playwright_TimeoutError

from custom_exception import *
from for_parser import *

import asyncio
import json
import time 
import random
import threading

atms_proxy = {}

async def main(brands: list, nums: list, proxies: list, time: float):
    '''
    Парсер
    brands - бренды, которые указываются в url make=
    num - артикулы, который указываются в url detailNum=
    proxies - список с прокси, который выбираются случайно
    
    Берем первые 30 товаров, сортируем их по дате доставки и записываем минимальную цену из 10 первых отсортированных цен по дате
    '''
    global atms_proxy
    k = 0
    for brand, num in zip(brands, nums):
        unsort_list_for_goods = []
        proxy_ban = []

        if proxies == []:
            print("У вас закончились прокси!")
            break
        else:

            proxy = random.choice(proxies)
            await asyncio.sleep(time)

            if ''.join(proxy) not in atms_proxy:
                atms_proxy[''.join(proxy)] = 0

            url = f"https://emex.ru/api/search/search?make={create_params_for_url(brand)}&detailNum={num}&locationId=38760&showAll=true&longitude=37.8613&latitude=55.7434"
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(proxy={'server': proxy[0], 'username': proxy[1], 'password': proxy[2]}, headless=False)
                    page = await browser.new_page()
                    try:
                        await page.goto(url, timeout=3333)
                    except playwright_TimeoutError:
                        await page.reload()

                    await page.mouse.wheel(0, 15000)
                    try:
                        await page.wait_for_selector('pre', timeout=3333)
                        pre = await (await page.query_selector("pre")).text_content()
                        response_data = dict(json.loads(pre))
                        if "originals" not in response_data["searchResult"]:
                            raise NoneException                            

                        k += 1
                        for i in range(30):
                            try:
                                data = response_data["searchResult"]["originals"][0]["offers"][i]
                                quantity = data["data"]["maxQuantity"]["value"]
                                date = data["delivery"]["value"]
                                price = data["displayPrice"]["value"]

                                offer_key_for_logo = data["data"]["offerKey"]
                                try:
                                    await page.goto(f'https://emex.ru/api/search/rating?offerKey={offer_key_for_logo}', timeout=3333)
                                except playwright_TimeoutError:
                                    try:
                                        await page.reload()
                                    except:
                                        await page.reload()

                                await page.wait_for_selector('pre', timeout=3333)

                                pre_logo = await (await page.query_selector("pre")).text_content()
                                logo_data = dict(json.loads(pre_logo))

                                logo = logo_data["priceLogo"]

                                unsort_list_for_goods.append([quantity, date, price, logo])
                            except IndexError:
                                break
                            except playwright_TimeoutError:
                                # print(i, "error1", url)
                                brands.append(brand)
                                nums.append(num)
                                atms_proxy[''.join(proxy)] += 1
                            # except Exception as e:
                                # print("thiiiiis", e)
                                # brands.append(brand)
                                # nums.append(num)
                    except playwright_TimeoutError:
                        # print("error2", url)
                        brands.append(brand)
                        nums.append(num)
                        atms_proxy[''.join(proxy)] += 1

                    if unsort_list_for_goods != []:
                        min_price_and_data = min(quick_sort(unsort_list_for_goods, 1)[:10], key=lambda x: x[2]) 
                        with open('parser/data.txt', 'a', encoding="UTF-8") as file:
                            file.write(f"{brand} {num} | Количество товара: {min_price_and_data[0]} Дата: {min_price_and_data[1]} Цена: {min_price_and_data[2]} Лого: {min_price_and_data[3]}\n")
                    else: 
                        # print('this) 1', brand)
                        brands.append(brand)
                        nums.append(num)
                    await browser.close()

                    if atms_proxy[''.join(proxy)] >= 20:
                        if proxy in proxies:
                            proxies.remove(proxy)
                        proxy_ban.append(proxy)
            except NoneException as e:
                print(e)
                continue
            except Exception as e:
                # print('this) 2', brand, num)
                brands.append(brand)
                nums.append(num)
                atms_proxy[''.join(proxy)] += 1
                if atms_proxy[''.join(proxy)] >= 20:
                    if proxy in proxies:
                        proxies.remove(proxy)
                    proxy_ban.append(proxy)

    print("_____", k)
    print(proxy_ban)

def run(brands, nums, proxies, time):
    asyncio.run(main(brands, nums, proxies, time))

def start():
    start = time.perf_counter()

    # ag_brand = []
    # ag_num = []
 


 
    proxies = [
        # ["http://94.158.190.96:1050", "LorNNF", "fr4B7cGdyS"],
        ["http://193.58.168.161:1050", "LorNNF", "fr4B7cGdyS"],
    ]

    brands = ["Peugeot---Citroen", "Mahle---Knecht", "Peugeot---Citroen", "Peugeot---Citroen", "Peugeot---Citroen", "Peugeot---Citroen", "ГАЗ", "VAG", "Autocomponent"] * 3
    # brands = ["Autocomponent"]
    nums = ["82026", "02943N0", "362312", "00004254A2", "00006426YN", "00008120T7", "6270000290", "016409399B", "01М21С9"] * 3
    # nums = ["01М21С9"]
    brands_split = split_file_for_thr(1, brands)
    nums_split = split_file_for_thr(1, nums)

    threadings = []
    for i in range(len(brands_split)):
        thread = threading.Thread(target=run, args=(brands_split[i], nums_split[i], proxies, float(i/10)), name=f"thr-{i}")
        thread.start()
        threadings.append(thread)

    for thread in threadings:
        thread.join()

    # run(ag_brand, ag_num, proxies)

    print(time.perf_counter() - start)


if __name__ == "__main__":
    start()