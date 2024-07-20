import requests
import json
import time
import random
import threading

from math import ceil
from urls import urls


def main(urls, headers, proxy):
    price_minimum = 10**10
    m_quantity = ""
    m_date = ""
    m_logo = ""
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=5, proxies=proxy)
            response_text = response.text
            response_json = json.loads(response_text)
            response_dict = dict(response_json)

            print("/\/\/\/\/\/\/\/\/\/\/")
            print(url)
            for i in range(10):
                try:
                    data = response_dict["searchResult"]["originals"][0]["offers"][i]
                    quantity = data["data"]["maxQuantity"]["value"]
                    date = data["delivery"]["value"]
                    price = data["displayPrice"]["value"]

                    offer_key_for_logo = data["data"]["offerKey"]
                    response_for_logo = requests.get(f'https://emex.ru/api/search/rating?offerKey={offer_key_for_logo}', headers=headers, timeout=5, proxies=proxy)
                    response_for_logo_text = response_for_logo.text
                    response_for_logo_json = json.loads(response_for_logo_text)
                    response_dict_for_logo = dict(response_for_logo_json)

                    logo = response_dict_for_logo["priceLogo"]

                    if int(price) < price_minimum:
                        price_minimum = int(price)
                        m_quantity = quantity
                        m_date = date
                        m_logo = logo
                except IndexError as e:
                    break
                except Exception as e:
                    print("warn2")
                    print(e)
        except Exception as e:
            print(url, "warn1")
            print(e)

        if price_minimum < 10**10:
            with open("parser/t.txt", "a", encoding="UTF-8") as file:
                file.write(f"Количество товара: {m_quantity} Дата: {m_date} Цена: {price_minimum} Лого: {m_logo}")
                file.write("\n")

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

start = time.perf_counter()

brands = ["Peugeot+%2F+Citroen", "Mahle---Knecht", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "%D0%93%D0%90%D0%97", "VAG", "Autocomponent"] * 10
nums = ["82026", "02943N0", "362312", "00004254A2", "00006426YN", "00008120T7", "6270000290", "016409399B", "01М21С9"] * 10
urls = urls

useragents = [ua.replace("\n", "") for ua in open('parser/useragents.txt').readlines()]

with open("parser/new_proxy.txt") as file:
    proxies = [proxy.replace("\n", "") for proxy in file.readlines()] 

for_thr = split_file_for_thr(16, urls)
thrs = []
i = 1
for urls in for_thr:
    proxy = random.choice(proxies)
    proxycool = {
        "http": proxy,
        "https": proxy
    }
    thr = threading.Thread(target=main, args=(urls, {"User-Agent": random.choice(useragents)}, proxycool), name=f"thr-{i}")
    thr.start()
    thrs.append(thr)
    i += 1

for thr in thrs:
    thr.join()

# for brand, num in zip(brands, nums):
#     headers = {'User-Agent': random.choice(useragents).replace('\n', '')}
#     proxy = random.choice(proxies)
#     proxy_for_req = {
#         "http": proxy,
#         "https": proxy  
#     }
#     thr = threading.Thread(target=main, args=(brand, num, headers, proxy_for_req))
#     thr.start()
#     thrs.append(thr)

# for thr in thrs:
#     thr.join()

print(time.perf_counter()-start)