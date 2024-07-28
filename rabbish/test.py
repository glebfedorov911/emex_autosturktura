# # import requests
# # import json
# # import time
# # import random
# # import threading

# # from math import ceil
# # from urls import urls


# # def main(urls, headers, proxy):
# #     price_minimum = 10**10
# #     m_quantity = ""
# #     m_date = ""
# #     m_logo = ""
# #     for url in urls:
# #         try:
# #             response = requests.get(url, headers=headers, timeout=5, proxies=proxy)
# #             response_text = response.text
# #             response_json = json.loads(response_text)
# #             response_dict = dict(response_json)

# #             print("/\/\/\/\/\/\/\/\/\/\/")
# #             print(url)
# #             for i in range(10):
# #                 try:
# #                     data = response_dict["searchResult"]["originals"][0]["offers"][i]
# #                     quantity = data["data"]["maxQuantity"]["value"]
# #                     date = data["delivery"]["value"]
# #                     price = data["displayPrice"]["value"]

# #                     offer_key_for_logo = data["data"]["offerKey"]
# #                     response_for_logo = requests.get(f'https://emex.ru/api/search/rating?offerKey={offer_key_for_logo}', headers=headers, timeout=5, proxies=proxy)
# #                     response_for_logo_text = response_for_logo.text
# #                     response_for_logo_json = json.loads(response_for_logo_text)
# #                     response_dict_for_logo = dict(response_for_logo_json)

# #                     logo = response_dict_for_logo["priceLogo"]

# #                     if int(price) < price_minimum:
# #                         price_minimum = int(price)
# #                         m_quantity = quantity
# #                         m_date = date
# #                         m_logo = logo
# #                 except IndexError as e:
# #                     break
# #                 except Exception as e:
# #                     print("warn2")
# #                     print(e)
# #         except Exception as e:
# #             print(url, "warn1")
# #             print(e)

# #         if price_minimum < 10**10:
# #             with open("parser/t.txt", "a", encoding="UTF-8") as file:
# #                 file.write(f"Количество товара: {m_quantity} Дата: {m_date} Цена: {price_minimum} Лого: {m_logo}")
# #                 file.write("\n")

# # def split_file_for_thr(num: int, url: list) -> list[list]:
# #     '''
# #     num - число потоков # например 4
# #     url - список с url => [...] # 16 штук
# #     list[list] - список со списками url => [[...]] # 4 по 4 
# #     '''
# #     new_url = []
# #     step = ceil(len(url)/num)
# #     for i in range(0, len(url), step):
# #         if i+step > len(url)-1:
# #             new_url.append(url[i:])
# #         else:
# #             new_url.append(url[i:i+step])

# #     return new_url

# # start = time.perf_counter()

# # brands = ["Peugeot+%2F+Citroen", "Mahle---Knecht", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "%D0%93%D0%90%D0%97", "VAG", "Autocomponent"] * 10
# # nums = ["82026", "02943N0", "362312", "00004254A2", "00006426YN", "00008120T7", "6270000290", "016409399B", "01М21С9"] * 10
# # urls = urls

# # useragents = [ua.replace("\n", "") for ua in open('parser/useragents.txt').readlines()]

# # with open("parser/new_proxy.txt") as file:
# #     proxies = [proxy.replace("\n", "") for proxy in file.readlines()] 

# # for_thr = split_file_for_thr(16, urls)
# # thrs = []
# # i = 1
# # for urls in for_thr:
# #     proxy = random.choice(proxies)
# #     proxycool = {
# #         "http": proxy,
# #         "https": proxy
# #     }
# #     thr = threading.Thread(target=main, args=(urls, {"User-Agent": random.choice(useragents)}, proxycool), name=f"thr-{i}")
# #     thr.start()
# #     thrs.append(thr)
# #     i += 1

# # for thr in thrs:
# #     thr.join()

# # # for brand, num in zip(brands, nums):
# # #     headers = {'User-Agent': random.choice(useragents).replace('\n', '')}
# # #     proxy = random.choice(proxies)
# # #     proxy_for_req = {
# # #         "http": proxy,
# # #         "https": proxy  
# # #     }
# # #     thr = threading.Thread(target=main, args=(brand, num, headers, proxy_for_req))
# # #     thr.start()
# # #     thrs.append(thr)

# # # for thr in thrs:
# # #     thr.join()

# # print(time.perf_counter()-start)

from playwright.async_api import async_playwright, TimeoutError as playwright_TimeoutError

import asyncio
import json
import time 
import random
import threading


def create_params_for_url(param: str):
    if "---" in param:
        param = param.replace("---", "+%2F+")
        return param
    return up.quote(param)

async def main(brands: list, nums: list, proxies: list):
    url = f"https://emex.ru/api/search/search?make={create_params_for_url(brands[0])}&detailNum={nums[0]}&locationId=38760&showAll=true&longitude=37.8613&latitude=55.7434"
    async with async_playwright() as p:
        browser = await p.chromium.launch(proxy={'server': proxy[0], 'username': proxy[1], 'password': proxy[2]}, headless=False)
        page = await browser.new_page()

        print(proxy)
        try:
            await page.goto(url, timeout=8000)
            input()
        except:
            print('not working')
        await browser.close()

brands = ["Peugeot---Citroen"]
nums = ["82026"]

proxies = [
    ["http://194.156.97.212:1050 ", "LorNNF", "fr4B7cGdyS"],
    ["http://194.156.123.115:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://109.248.166.189:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://91.188.244.80:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://193.58.168.161:1050", "LorNNF", "fr4B7cGdyS"],
] 

for proxy in proxies:
    asyncio.run(main(brands, nums, proxy))

# import requests
# import json


# API_KEY = "fea1d0c98a179dfc855b7255d801b7f0"
# URL = "https://api.dashboard.proxy.market"

# def check_balance():
#     url = URL + f"/dev-api/balance/{API_KEY}"
#     return requests.get(url).text

# def list_proxy():
#     url = URL + f"/dev-api/list/{API_KEY}"
#     data = {
#         "type": "ipv4",
#         "proxy_type": "server",
#         "page": 1,
#         "page_size": 100,
#         "sort": 1
#     }

#     return requests.post(url, json=data).text

# def buy_proxy():
#     url = URL + f"/dev-api/buy-proxy/{API_KEY}"
#     data = {
#         "PurchaseBilling": {
#             "count": 1,
#             "duration": 30,
#             "type": 100,
#             "country": "ru"
#         }
#     }

#     return requests.post(url, json=data).text

# def prolong_proxy():
#     url = URL + f"/dev-api/prolong/{API_KEY}"
#     data = {
#         "ProlongationForm": {
#             "duration": 30,
#             "proxies": "6460790"
#         }
#     }

#     return requests.post(url, json=data).text

# print(check_balance()) 
# print(list_proxy()) 
# print(buy_proxy())
# print(prolong_proxy())
