from fastapi import HTTPException, status

import asyncio
import json
import time
import random
import requests
import aiohttp
import threading

from .depends import *

from playwright.async_api import async_playwright


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

async def main(user_id):
    global user_data, user_locks
    user_locks[user_id] = threading.Lock()

    DEEP_FILTER = user_data[user_id]["filter"].deep_filter
    DEEP_ANALOG = user_data[user_id]["filter"].deep_analog
    ANALOG = user_data[user_id]["filter"].analog
    IS_BIGGER = user_data[user_id]["filter"].is_bigger 
    DATE = user_data[user_id]["filter"].date
    LOGO = user_data[user_id]["filter"].logo 
    PICKUP_POINT = user_data[user_id]["filter"].pickup_point
    browser = None
    # proxy = None
    user_data[user_id]["all_break"] = False
    user_data[user_id]["columns"] = ["Артикул", "Наименование", "Брэнд", "Артикул", "Кол-во", "Цена", "Партия", "НДС", "Лого", "Доставка", "Лучшая цена", "Количество",]

    if LOGO and "Цена с лого" not in user_data[user_id]["columns"]:
        user_data[user_id]["columns"].append("Цена с лого")

    while user_data[user_id]["status"] == "PARSER_RUNNING":
        headers = {'User-Agent': random.choice(USERAGENTS)}
        # if user_data[user_id]["proxies"] != []:
            # with user_locks[user_id]:
                # proxy = user_data[user_id]["proxies"].pop(random.randint(0, len(user_data[user_id]["proxies"])-1))
        
        if user_data[user_id]["all_break"]:
            user_data[user_id]["status"] = "Парсер не запущен"
            return

        for stop in user_data[user_id]["stop"]:
            if stop:
                print("Остановка парсера началась!")
                # if browser:
                #     await browser.close()
                return
        
        # try:
        #     proxy = [proxy.ip_with_port, proxy.login, proxy.password]
        # except:
        #     proxy = [proxy[0], proxy[1], proxy[2]]

        if len(user_data[user_id]["brands"]) == 0 or all([ev.is_set() for ev in user_data[user_id]["events"]]) or user_data[user_id]["all_break"]:
            user_data[user_id]["status"] = "Парсер не запущен"
            return

        with user_locks[user_id]:
            brand = user_data[user_id]["brands"].pop(0)
        if user_locks[user_id].locked():
            print(f"1. Поток {threading.current_thread().name} ожидает разблокировки")
        else:
            print(f"1. Поток {threading.current_thread().name} не блокирован")

        url = f"https://emex.ru/api/search/search?make={create_params_for_url(brand[2])}&detailNum={brand[0]}&locationId={PICKUP_POINT}&showAll=true&longitude=37.8613&latitude=55.7434"
        
        # async with async_playwright() as p:
        try:
            for_log = f"-=-=-=-=-=-=-={threading.current_thread().name}=-=-=-=-=-=-=-"
            print(for_log)
            if user_data[user_id]["count_brands"] == 0:
                user_data[user_id]["count_brands"] = 1
            print(int(len(user_data[user_id]["excel_result"]) / user_data[user_id]["count_brands"] * 100))
            print(user_data[user_id]["status"])
            # print("URL сейчас:", url, '\n', proxy, user_data[user_id]["count_proxies"], '\n', "Количество в бане:", len(user_data[user_id]["ban_list"]))
            print("URL сейчас:", url, '\n', user_data[user_id]["count_proxies"], '\n', "Количество в бане:", len(user_data[user_id]["ban_list"]))
            print("Данных спаршено:", len(user_data[user_id]["excel_result"]), "данных всего:", user_data[user_id]["count_brands"])
            print("Обновление списка (длина):", len(user_data[user_id]["brands"]))
            print("Потоки", threading.enumerate())
            try:
                print(*[f"""{i} | {user_data[user_id]["threads"][i]}: {user_data[user_id]["threads"][i].is_alive()}""" for i in range(len(user_data[user_id]["threads"])) if user_data[user_id]["threads"][i] != None]) #4: {user_data[user_id]["threads"][4].is_alive()} 5: {user_data[user_id]["threads"][5].is_alive()}""")
            except Exception as e:
                print("Ошибка в alive модуле", e)
            print(f"-="*(len(for_log)//2))

            # for i in range(len(user_data[user_id]["threads"])):
            #     if (not (user_data[user_id]["threads"][i] is None)):
            #         if not user_data[user_id]["threads"][i].is_alive():
            #             with user_locks[user_id]:
            #                 if proxy:
            #                     with user_locks[user_id]:
            #                         user_data[user_id]["proxies"].append(proxy)
            #                         user_data[user_id]["brands"].append(brand)
            #                     proxy = None
            #                     continue
            #     else:
            #         if proxy:
            #             with user_locks[user_id]:
            #                 user_data[user_id]["proxies"].append(proxy)
            #                 user_data[user_id]["brands"].append(brand)
            #             proxy = None
            #             continue

            # proxies = {
            #     'http': 'http://n66063054a6f17c192a006d-zone-custom-region-ru:b151e67bc2b9462683bdab5eb1ff4acc@p1.mangoproxy.com:2333',
            #     # 'https': 'https://n66063054a6f17c192a006d-zone-custom-region-ru:b151e67bc2b9462683bdab5eb1ff4acc@p1.mangoproxy.com:2333'
            # }

            # proxies = {
            # "http': http://n66063054a6f17c192a006d-zone-custom-region-ru:b151e67bc2b9462683bdab5eb1ff4acc@p1.mangoproxy.com:2333',
            # "https': http://n66063054a6f17c192a006d-zone-custom-region-ru:b151e67bc2b9462683bdab5eb1ff4acc@p1.mangoproxy.com:2333',
            # }

            proxies = 'http://n66063054a6f17c192a006d-zone-custom-region-ru:b151e67bc2b9462683bdab5eb1ff4acc@p1.mangoproxy.com:2333'
            # browser = requests.get(url, proxies=proxies, headers=headers)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, proxy=proxies, headers=headers) as resp:
                    response = await resp.json()

            # browser = await p.chromium.launch(
            #     headless=False,
            #     proxy={
            #         "server": "http://p1.mangoproxy.com:2333", #proxy[0],
            #         "username": "n66063054a6f17c192a006d-zone-custom-region-ru", #proxy[1],
            #         "password": "b151e67bc2b9462683bdab5eb1ff4acc", #proxy[2],
            #     },
            #     timeout=7777
            # )
            # page = await browser.new_page(user_agent=random.choice(USERAGENTS))

            # try:
            #     await page.goto(url, timeout=4444)
            # except Exception as e:
            #     print("С первой попытки не удалось! Вторая загрузки страницы попытка...")
            #     await page.goto(url, timeout=4444)

            # pre = await (await page.query_selector("pre")).text_content()
            # response = dict(json.loads(browser.text))
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
                    result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], 0, 0, 0, 0,]
                    if LOGO:
                        result.append(0)
                if "replacements" in response["searchResult"]:
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
                    result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], 0, 0, 0, 0,]
                    if LOGO:
                        result.append(0)

                if "replacements" in response["searchResult"]:
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
                result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], 0, 0, 0, 0,]
                if LOGO:
                    result.append(0)
                with user_locks[user_id]:
                    user_data[user_id]["excel_result"].append(result)
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

                # try:
                #     await page.goto(
                #         f"https://emex.ru/api/search/rating?offerKey={best_data[0]}",
                #         timeout=4444,
                #     )
                # except:
                #     print("Вторая попытка загрузить страницу с лого...")
                #     await page.goto(
                #         f"https://emex.ru/api/search/rating?offerKey={best_data[0]}",
                #         timeout=4444,
                #     )
                # req = requests.get(f"https://emex.ru/api/search/rating?offerKey={best_data[0]}", proxies=proxies)

                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://emex.ru/api/search/rating?offerKey={best_data[0]}", proxy=proxies, headers=headers) as resp:
                        response_with_logo = await resp.json()
                
                # pre_with_logo = await (
                #     await page.query_selector("pre")
                # ).text_content()
                # response_with_logo = dict(json.loads(req.text))
                price_logo = response_with_logo["priceLogo"]

                result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], price_logo, *best_data[1:],]
                if LOGO:
                    best_data = None
                    sorted_by_price = quick_sort(originals, 2)[:20]
                    for data in sorted_by_price:
                        # try:
                        #     await page.goto(
                        #         f"https://emex.ru/api/search/rating?offerKey={data[0]}",
                        #         timeout=4444,
                        #     )
                        # except:
                        #     print("Вторая попытка загрузить лого (фильтр с лого)...")
                        #     await page.goto(
                        #         f"https://emex.ru/api/search/rating?offerKey={data[0]}",
                        #         timeout=4444,
                        #     )

                        # req = requests.get(f"https://emex.ru/api/search/rating?offerKey={best_data[0]}", proxies=proxies)
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f"https://emex.ru/api/search/rating?offerKey={data[0]}", proxy=proxies, headers=headers) as resp:
                                response_with_logo = await resp.json()
                        # pre_with_logo = await (
                        #     await page.query_selector("pre")
                        # ).text_content()
                        # response_with_logo = dict(json.loads(req.text))
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
                if user_locks[user_id].locked():
                    print(f"3. Поток {threading.current_thread().name} ожидает разблокировки")
                else:
                    print(f"3. Поток {threading.current_thread().name} не блокирован")
            # with user_locks[user_id]:
            #     user_data[user_id]["proxies"].append(proxy)
        except Exception as e:
            print("-="*20)
            print("Общее исключение\nОшибка:", e)
            print("-="*20)
            with user_locks[user_id]:
                user_data[user_id]["brands"].append(brand)
            if user_locks[user_id].locked():
                print(f"4. Поток {threading.current_thread().name} ожидает разблокировки")
            else:
                print(f"4. Поток {threading.current_thread().name} не блокирован")
                # user_data[user_id]["ban_list"].append("@".join(proxy))

            # if user_data[user_id]["proxies"] != []:
            #     with user_locks[user_id]:
            #         proxy = user_data[user_id]["proxies"].pop(0)
            #     try:
            #         proxy = [proxy.ip_with_port, proxy.login, proxy.password]
            #     except:
            #         proxy = [proxy[0], proxy[1], proxy[2]]
            # else:
            #     break
            # #30     42
            # if user_data[user_id]["count_proxies"]-user_data[user_id]["count_of_threadings"] < len(user_data[user_id]["ban_list"]) < user_data[user_id]["count_proxies"]+user_data[user_id]["count_of_threadings"]:
            #     user_data[user_id]["count_proxies"] = len(user_data[user_id]["ban_list"])
            #     user_data[user_id]["all_break"] = True
            #     raise HTTPException(
            #         status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            #         detail="Закочнились прокси",
            #     )
            #     break
# with user_locks[user_id]:
#     if proxy:
#         user_data[user_id]["proxies"].append(proxy)
# if browser:
#     await browser.close()

def run(user_id):
    asyncio.run(main(user_id))

# # import requests
# # import json 


# # url = f"https://emex.ru/api/search/search?make=FUCHS&detailNum=0004721003&locationId=38760&showAll=true&longitude=37.8613&latitude=55.7434"
        
# # proxies = {
# #     'http': 'http://n66063054a6f17c192a006d-zone-custom-region-ru:b151e67bc2b9462683bdab5eb1ff4acc@p1.mangoproxy.com:2333',
# #     # 'https': 'https://n66063054a6f17c192a006d-zone-custom-region-ru:b151e67bc2b9462683bdab5eb1ff4acc@p1.mangoproxy.com:2333'
# # }
# # browser = requests.get(url, timeout=4, proxies=proxies)
# # response = dict(json.loads(browser.text))
# # print(response)#FUCHS	0004721003



# import aiohttp
# import asyncio

# url = f"https://emex.ru/api/search/search?make=FUCHS&detailNum=0004721003&locationId=38760&showAll=true&longitude=37.8613&latitude=55.7434"
# proxies = 'http://n66063054a6f17c192a006d-zone-custom-region-ru:b151e67bc2b9462683bdab5eb1ff4acc@p1.mangoproxy.com:2333'
# response = ''
# async def fetch():
#     global response
#     async with aiohttp.ClientSession() as session:
#             async with session.get(url, proxy=proxies) as resp:
#                 rest = await resp.json()

#     print(rest)

# if __name__ == "__main__":
#     asyncio.run(fetch())