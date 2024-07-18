import asyncio
import time
import os
import threading

from math import ceil
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from urllib.parse import quote


os.system("taskkill /im chromium.exe /f")

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

async def main(url: str, http, us, ps) -> None:
    atms = 0
    while url != []:
        if url == []:
            break

        async with async_playwright() as p:
            browser = None
            try:
                browser = await p.chromium.launch(proxy={'server': http, 'username': us, 'password': ps}, headless=True)
                # browser = await p.chromium.launch(headless=True)

                page = await browser.new_page()
                await page.goto(url[0])
                
                try:
                    await page.wait_for_selector('.sc-7bab7953-1.fQUPMo.e-titleH2.e-titleH2--themeDefault', timeout=3000)
                except:
                    await page.reload()
                    await page.wait_for_selector('.sc-7bab7953-1.fQUPMo.e-titleH2.e-titleH2--themeDefault', timeout=3000)

                if await page.query_selector_all('div[class="sc-f77e292d-0 jxaiPV"]') != []: 
                    await page.click('.sc-f77e292d-0.jxaiPV') #more
                if await page.query_selector_all("h2[class='sc-4613b6b1-2 dSXovO e-titleH2 e-titleH2--themeDefault']") != []:
                    with open('parser/new3.txt', 'a', encoding="UTF-8") as file:
                        file.write(f'{url[0]} | ТОВАРА НЕТ В НАЛИЧИИ')
                        file.write('\n')
                    url.pop(0)
                    continue
                
                try:
                    await page.wait_for_selector(".sc-129a3fbb-0.sc-129a3fbb-6.fZObHF.gTiXml", timeout=3000)
                except:
                    await page.reload()
                    await page.click('.sc-f77e292d-0.jxaiPV') #more
                    await page.wait_for_selector(".sc-129a3fbb-0.sc-129a3fbb-6.fZObHF.gTiXml", timeout=3000)

                price = await (await page.query_selector('div[class="sc-129a3fbb-0 sc-129a3fbb-6 fZObHF gTiXml"]')).text_content()
                
                try:
                    await page.wait_for_selector(".sc-129a3fbb-0.sc-129a3fbb-10.fZObHF.cFcOfg", timeout=3000)
                except:
                    await page.reload()
                    await page.click('.sc-f77e292d-0.jxaiPV') #more
                    await page.wait_for_selector(".sc-129a3fbb-0.sc-129a3fbb-10.fZObHF.cFcOfg", timeout=3000)   
                
                date = await (await page.query_selector('div[class="sc-129a3fbb-0 sc-129a3fbb-10 fZObHF cFcOfg"]')).text_content()
                
                try:
                    await page.wait_for_selector('div[class="sc-45c0335-3 ecqRRC"]', timeout=3000)
                except:
                    await page.reload()
                    await page.click('.sc-f77e292d-0.jxaiPV') #more
                    await page.wait_for_selector('div[class="sc-45c0335-3 ecqRRC"]', timeout=3000)

                await (await page.query_selector('div[class="sc-45c0335-3 ecqRRC"]')).click() #score
                
                try:
                    await page.wait_for_selector(".sc-4599f03e-2.feGyYA", timeout=3000)
                except:
                    await page.reload()
                    await page.click('.sc-f77e292d-0.jxaiPV') #more
                    await page.wait_for_selector(".sc-4599f03e-2.feGyYA", timeout=3000)

                brand = await (await page.query_selector('div[class="sc-4599f03e-2 feGyYA"]')).text_content()

                with open('parser/new3.txt', 'a', encoding="UTF-8") as file:
                    file.write(f'{url[0]} | price: {"".join(price.split()[:-1])} | date: {date.split()[0]} | brand: {brand.split()[1][:4]}')
                    file.write('\n')
                url.pop(0)
        
            
            except Exception as e:
                with open('parser/new3.txt', 'a', encoding="UTF-8") as file:
                    file.write(f"{url[0]} | ОШИБКА")
                    file.write('\n')
                if atms < 3:
                    url.append(url[0])
                    url.pop(0)
                    atms += 1
                    print(e)
                    print(atms)
                    continue
                atms = 0
                print("all atms")

            if browser: await browser.close()

def run(url, http, us, ps):
    asyncio.run(main(url, http, us, ps))

if __name__ == '__main__':
    t = time.perf_counter()
    
    url = [
        "https://emex.ru/products/82026/peugeot---citroen/38760",
        "https://emex.ru/products/362312/peugeot---citroen/38760",
        "https://emex.ru/products/00004254A2/peugeot---citroen/38760",
        "https://emex.ru/products/00006426YN/peugeot---citroen/38760",  
        "https://emex.ru/products/00008120T7/peugeot---citroen/38760",
        "https://emex.ru/products/6270000290/ГАЗ/38760",
        "https://emex.ru/products/016409399B/VAG/38760",
        "https://emex.ru/products/01М21С9/Autocomponent/38760", 
        "https://emex.ru/products/2113/FEBI/38760",
        "https://emex.ru/products/281006035/BOSCH/38760",
        "https://emex.ru/products/02943N0/Mahle---Knecht/38760",
        "https://emex.ru/products/0320L8/Peugeot---Citroen/38760",  
        "https://emex.ru/products/03AC0361/A-GRESSOR/38760",
        "https://emex.ru/products/4244501/Sampa/38760",
        "https://emex.ru/products/4310401/Sampa/38760",
        "https://emex.ru/products/04C905616D/MOTEC/38760",
    ] * 8

    proxy = [
        ["http://194.35.113.239:1050", "2Q3n1o", "FjvCaesiwS"],
        ["http://188.130.210.107:1050", "2Q3n1o", "FjvCaesiwS"],
        ["http://109.248.139.54:1050", "2Q3n1o", "FjvCaesiwS"],
        ["http://185.181.245.74:1050", "2Q3n1o", "FjvCaesiwS"],
    ] * ceil(128/4) 

    THS = 8
    url = split_file_for_thr(THS, url)

    thrs = []
    k = 1
    for n in range(THS):
        p = proxy[n]
        thr = threading.Thread(target=run, args=(url[n], *p), name=f'thr-{k}')
        thr.start()
        thrs.append(thr)

        k += 1

    for thr in thrs:
        thr.join()

    print(time.perf_counter()-t) 
    os.system("taskkill /im chromium.exe /f")