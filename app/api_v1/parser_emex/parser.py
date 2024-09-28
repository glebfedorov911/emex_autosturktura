from fastapi import HTTPException, status

import asyncio
import json
import time
import random
import threading

from .depends import *

from playwright.async_api import async_playwright


user_data = {}

# {"threads": threads.copy(), "events": [Event() for _ in range(count_of_threadings)],
# "proxies": proxies, "filter": filter, "excel_result": [], "status": "Парсер не запущен",
# "count_proxies": len(proxies), "ban_list": set()}

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
    global user_data, user_lock
    user_locks[user_id] = threading.Lock()

    DEEP_FILTER = user_data[user_id]["filter"].deep_filter
    DEEP_ANALOG = user_data[user_id]["filter"].deep_analog
    ANALOG = user_data[user_id]["filter"].analog
    IS_BIGGER = user_data[user_id][
        "filter"
    ].is_bigger  # True - больше False - меньше None - не указано
    DATE = user_data[user_id]["filter"].date
    LOGO = user_data[user_id]["filter"].logo  # HXAW - пример лого None - Без лого
    PICKUP_POINT = user_data[user_id]["filter"].pickup_point
    user_data[user_id]["is_using_testproxy"][threading.current_thread().name] = True 
    user_data[user_id]["columns"] = [
        "Артикул",
        "Наименование",
        "Брэнд",
        "Артикул",
        "Кол-во",
        "Цена",
        "Партия",
        "НДС",
        "Лого",
        "Доставка",
        "Лучшая цена",
        "Количество",
    ]

    if LOGO and "Цена с лого" not in user_data[user_id]["columns"]:
        user_data[user_id]["columns"].append("Цена с лого")

    if user_data[user_id]["proxies"] != []:
        proxy = user_data[user_id]["proxies"].pop(0)
        try:
            proxy = [proxy.ip_with_port, proxy.login, proxy.password]
        except:
            proxy = [proxy[0], proxy[1], proxy[2]]
    else:
        proxy = ["http://test:8888", "user1", "pass1"]
    atms = 0
    while True:
        if len(user_data[user_id]["brands"]) == 0:
            break
        with user_locks[user_id]:
            brand = user_data[user_id]["brands"].pop(0)
        if all([ev.is_set() for ev in user_data[user_id]["events"]]):
            break

        url = f"https://emex.ru/api/search/search?make={create_params_for_url(brand[2])}&detailNum={brand[0]}&locationId={PICKUP_POINT}&showAll=true&longitude=37.8613&latitude=55.7434"
        async with async_playwright() as p:
            try:
                print(f"-=-=-=-=-=-=-={threading.current_thread().name}=-=-=-=-=-=-=-")
                print("url_now: ", url, '\n', proxy, user_data[user_id]["count_proxies"], '\n', user_data[user_id]["ban_list"])
                print(len(user_data[user_id]["excel_result"]), user_data[user_id]["count_brands"])
                print(user_data[user_id]["is_using_testproxy"])
                print(len(user_data[user_id]["brands"]))
                print(f"""0: {user_data[user_id]["thread"][0].is_alive()} 1: {user_data[user_id]["thread"][1].is_alive()} 2: {user_data[user_id]["thread"][2].is_alive()}\n
                3: {user_data[user_id]["thread"][3].is_alive()} 4: {user_data[user_id]["thread"][4].is_alive()} 5: {user_data[user_id]["thread"][5].is_alive()}""")
                print(f"-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
                browser = await p.chromium.launch(
                    headless=True,
                    proxy={
                        "server": proxy[0],
                        "username": proxy[1],
                        "password": proxy[2],
                    },
                    timeout=7777
                )
                page = await browser.new_page(user_agent=random.choice(USERAGENTS))

                try:
                    await page.goto(url, timeout=4444)
                except:
                    await page.goto(url, timeout=4444)

                pre = await (await page.query_selector("pre")).text_content()
                response = dict(json.loads(pre))
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
                        result = [
                            brand[0],
                            brand[1],
                            brand[2],
                            brand[3],
                            brand[4],
                            brand[5],
                            brand[6],
                            brand[7],
                            0,
                            0,
                            0,
                            0,
                        ]
                        if LOGO:
                            result.append(0)
                        # continue

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
                        result = [
                            brand[0],
                            brand[1],
                            brand[2],
                            brand[3],
                            brand[4],
                            brand[5],
                            brand[6],
                            brand[7],
                            0,
                            0,
                            0,
                            0,
                        ]
                        if LOGO:
                            result.append(0)
                        # continue

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
                    result = [
                        brand[0],
                        brand[1],
                        brand[2],
                        brand[3],
                        brand[4],
                        brand[5],
                        brand[6],
                        brand[7],
                        0,
                        0,
                        0,
                        0,
                    ]
                    if LOGO:
                        result.append(0)
                    with user_locks[user_id]:
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
                    for idx in range(len(best_data)):
                        try:
                            best_data[idx] = int(best_data[idx])
                        except:
                            pass

                    try:
                        await page.goto(
                            f"https://emex.ru/api/search/rating?offerKey={best_data[0]}",
                            timeout=4444,
                        )
                    except:
                        await page.goto(
                            f"https://emex.ru/api/search/rating?offerKey={best_data[0]}",
                            timeout=4444,
                        )

                    pre_with_logo = await (
                        await page.query_selector("pre")
                    ).text_content()
                    response_with_logo = dict(json.loads(pre_with_logo))
                    price_logo = response_with_logo["priceLogo"]

                    # result = [price_logo, *best_data[1:]]
                    result = [
                        brand[0],
                        brand[1],
                        brand[2],
                        brand[3],
                        brand[4],
                        brand[5],
                        brand[6],
                        brand[7],
                        price_logo,
                        *best_data[1:],
                    ]
                    if LOGO:
                        best_data = None
                        sorted_by_price = quick_sort(originals, 2)[:20]
                        for data in sorted_by_price:
                            try:
                                await page.goto(
                                    f"https://emex.ru/api/search/rating?offerKey={data[0]}",
                                    timeout=4444,
                                )
                            except:
                                await page.goto(
                                    f"https://emex.ru/api/search/rating?offerKey={data[0]}",
                                    timeout=4444,
                                )

                            # while atms <= 5:
                            #     try:
                            #         await page.goto(f"https://emex.ru/api/search/rating?offerKey={data[0]}", timeout=3333)
                            #     except:
                            #         atms += 1

                            # print(brand, atms)
                            # if atms >= 5:
                            #     raise Exception
                            # else:
                            #     atms = 0

                            pre_with_logo = await (
                                await page.query_selector("pre")
                            ).text_content()
                            response_with_logo = dict(json.loads(pre_with_logo))
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
            except Exception as e:
                print(e)
                with user_locks[user_id]:
                    user_data[user_id]["brands"].append(brand)
                atms += 1

                if proxy != ["http://test:8888", "user1", "pass1"]:
                    with user_locks[user_id]:
                        user_data[user_id]["ban_list"].add("@".join(proxy))
                    user_data[user_id]["is_using_testproxy"][threading.current_thread().name] = False
                else:
                    user_data[user_id]["is_using_testproxy"][threading.current_thread().name] = True
                if user_data[user_id]["proxies"] != []:
                    with user_locks[user_id]:
                        proxy = user_data[user_id]["proxies"].pop(0)
                    try:
                        proxy = [proxy.ip_with_port, proxy.login, proxy.password]
                    except:
                        proxy = [proxy[0], proxy[1], proxy[2]]
                else:
                    proxy = ["http://test:8888", "user1", "pass1"]

                if user_data[user_id]["count_proxies"] == len(user_data[user_id]["ban_list"]):
                    print(user_data[user_id]["count_proxies"], len(user_data[user_id]["ban_list"]))
                    raise HTTPException(
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                        detail="Закочнились прокси",
                    )
                    break

                if user_data[user_id]["count_proxies"] == len(user_data[user_id]["ban_list"]) + user_data[user_id]["is_using_testproxy"].count(False):
                    user_data[user_id]["count_proxies"] = len(user_data[user_id]["ban_list"])
                    raise HTTPException(
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                        detail="Закочнились прокси",
                    )
                    break

                if all([user_data[user_id]["is_using_testproxy"][name_thr] for name_thr in user_data[user_id]["is_using_testproxy"]]):
                    raise HTTPException(
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                        detail="Закочнились прокси",
                    )
                    break

                if sum([1 for proxy_check in user_data[user_id]["PROXIES"] if proxy_check in user_data[user_id]["ban_list"]]) == user_data[user_id]["count_proxies"] and user_data[user_id]["PROXIES"] != []:
                    print(user_data[user_id]["count_proxies"], len(user_data[user_id]["ban_list"]))
                    raise HTTPException(
                        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                        detail="Закочнились прокси",
                    )
                    break
                # if atms % 5 == 0:
    if proxy != ["http://test:8888", "user1", "pass1"]:
            user_data[user_id]["proxies"].append(proxy)
    user_data[user_id]["is_using_testproxy"][threading.current_thread().name] = True


def run(user_id):
    asyncio.run(main(user_id))
