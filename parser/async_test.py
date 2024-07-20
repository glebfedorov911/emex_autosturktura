import aiohttp
import asyncio
import json
import time
import random


async def get_json(session: aiohttp.ClientSession, brand: str, num: str, headers: dict, proxy: dict | None = None) -> None:
    url = f'https://emex.ru/api/search/search?make={brand}&detailNum={num}&locationId=38760&showAll=true&longitude=37.8613&latitude=55.7434'
    print("/\/\/\/\/\/\/\/\/\/\/")
    print(url)
    price_minimum = 10**10
    m_quantity = ""
    m_date = ""
    m_logo = ""
    async with session.get(url, headers=headers, proxy=proxy, timeout=4) as response:
        response_text = await response.text()
        response_json = json.loads(response_text)
        response_dict = dict(response_json)

        for i in range(10):
            try:
                data = response_dict["searchResult"]["originals"][0]["offers"][i]
                quantity = data["data"]["maxQuantity"]["value"]
                date = data["delivery"]["value"]
                price = data["displayPrice"]["value"]

                offer_key_for_logo = data["data"]["offerKey"]
                url2 = f'https://emex.ru/api/search/rating?offerKey={offer_key_for_logo}'
                async with session.get(url2, headers=headers, proxy=proxy, timeout=4) as response_for_logo:
                    response_for_logo_text = await response_for_logo.text()
                    response_for_logo_json = json.loads(response_for_logo_text)
                    response_dict_for_logo = dict(response_for_logo_json)

                    logo = response_dict_for_logo["priceLogo"]
                    time.sleep(0.2)

                # print("-=-=-=-=-=-=-=-=-=-=-")
                if int(price) < price_minimum:
                    price_minimum = int(price)
                    m_quantity = quantity
                    m_date = date
                    m_logo = logo

            except IndexError as e:
                break
    
    if price_minimum < 10**10:
        with open("parser/t.txt", "a", encoding="UTF-8") as file:
            file.write(f"Количество товара: {m_quantity} Дата: {m_date} Цена: {price_minimum} Лого: {m_logo}")
            file.write("\n")

async def parse(brands: list, nums: list,  headers: dict, proxies: list | None = None) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = []
        k = 0
        for brand, num in zip(brands, nums):
            tasks.append(get_json(session, brand, num, headers, proxies[k]))
            k += 1

        responses = await asyncio.gather(*tasks)
        return responses


start = time.perf_counter()

brands = ["Peugeot+%2F+Citroen", "Mahle---Knecht", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "%D0%93%D0%90%D0%97", "VAG", "Autocomponent"] * 10
nums = ["82026", "02943N0", "362312", "00004254A2", "00006426YN", "00008120T7", "6270000290", "016409399B", "01М21С9"] * 10

useragents = [ua for ua in open('parser/useragents.txt').readlines()]

proxies = [
    "http://2Q3n1o:FjvCaesiwS@213.226.101.138:1050",
    "http://2Q3n1o:FjvCaesiwS@46.8.222.226:1050",
    "http://2Q3n1o:FjvCaesiwS@109.248.143.65:1050",
    "http://2Q3n1o:FjvCaesiwS@46.8.212.110:1050",
    "http://2Q3n1o:FjvCaesiwS@95.182.125.217:1050",
    "http://2Q3n1o:FjvCaesiwS@46.8.23.9:1050",
] * 15

# for brand, num in zip(brands, nums):
headers = {'User-Agent': random.choice(useragents).replace('\n', '')}

loop = asyncio.get_event_loop()
responses = loop.run_until_complete(parse(brands, nums, headers, proxies))

for response in responses:
    response

print(time.perf_counter() - start)