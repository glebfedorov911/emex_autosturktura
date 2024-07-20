from playwright.async_api import async_playwright, TimeoutError as playwright_TimeoutError

import asyncio
import json
import time 
import random


async def main(brand, num, ip, username, password):
    url = f"https://emex.ru/api/search/search?make={brand}&detailNum={num}&locationId=38760&showAll=true&longitude=37.8613&latitude=55.7434"
    async with async_playwright() as p:
        browser = await p.chromium.launch(proxy={'server': ip, 'username': username, 'password': password}, headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.mouse.wheel(0, 15000)

        try:
            await page.wait_for_selector('pre', timeout=5000)
            pre = await (await page.query_selector("pre")).text_content()
            response_data = dict(json.loads(pre))
            
            print("\/" * 10)
            print(url)

            for i in range(10000):
                try:
                    data = response_data["searchResult"]["originals"][0]["offers"][i]
                    quantity = data["data"]["maxQuantity"]["value"]
                    date = data["delivery"]["value"]
                    price = data["displayPrice"]["value"]

                    offer_key_for_logo = data["data"]["offerKey"]
                    await page.goto(f'https://emex.ru/api/search/rating?offerKey={offer_key_for_logo}')
                    await page.wait_for_selector('pre', timeout=5000)
                    pre_logo = await (await page.query_selector("pre")).text_content()
                    logo_data = dict(json.loads(pre_logo))

                    logo = logo_data["priceLogo"]

                    print("-=" * 10)
                    print(f"{i+1}. Количество товара: {quantity} Дата: {date} Цена: {price} Лого: {logo}")
                except IndexError:
                    break
                except playwright_TimeoutError:
                    print("error", url)
        except playwright_TimeoutError:
            print("error", url)

        await browser.close()


if __name__ == "__main__":
    start = time.perf_counter()

    proxies = [
        ["http://194.35.113.239:1050", "2Q3n1o", "FjvCaesiwS"],
        ["http://188.130.210.107:1050", "2Q3n1o", "FjvCaesiwS"],
        ["http://109.248.139.54:1050", "2Q3n1o", "FjvCaesiwS"],
        ["http://185.181.245.74:1050", "2Q3n1o", "FjvCaesiwS"],
    ]

    proxy = random.choice(proxies)

    brands = ["Peugeot+%2F+Citroen", "Mahle---Knecht", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "Peugeot+%2F+Citroen", "%D0%93%D0%90%D0%97", "VAG", "Autocomponent"] * 10
    nums = ["82026", "02943N0", "362312", "00004254A2", "00006426YN", "00008120T7", "6270000290", "016409399B", "01М21С9"] * 10

    for brand, num in zip(brands, nums):
        asyncio.run(main(brand, num, proxy[0], proxy[1], proxy[2]))

    print(time.perf_counter() - start)