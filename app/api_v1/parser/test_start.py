from playwright.async_api import async_playwright, TimeoutError as playwright_TimeoutError
import pandas as pd

import asyncio
import json
import time 
import random
import threading

import urllib.parse as up

from math import ceil

start = time.perf_counter()

proxies = [
    ["http://46.8.16.194:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://194.156.123.115:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://109.248.166.189:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://91.188.244.80:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://193.58.168.161:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://46.8.22.63:1050", "LorNNF", "fr4B7cGdyS"],
    # ["http://46.8.10.206:1050", "2Q3n1o", "FjvCaesiwS"], #!!!
    ["http://109.248.14.248:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://2.59.50.242:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://94.158.190.152:1050", "LorNNF", "fr4B7cGdyS"],
    # ["http://188.130.188.9:1050", "2Q3n1o", "FjvCaesiwS"], #!!!
    ["http://188.130.129.128:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://31.40.203.252:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://45.15.73.112:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://46.8.157.208:1050", "LorNNF", "fr4B7cGdyS"],
    ["http://188.130.128.166:1050", "LorNNF", "fr4B7cGdyS"],
] 



def run(brands, nums):
    asyncio.run(main(brands, nums))

# brands = ["Peugeot---Citroen", "Mahle---Knecht", "Peugeot---Citroen", "Peugeot---Citroen", "Peugeot---Citroen", "Peugeot---Citroen", "ГАЗ", "VAG", "Autocomponent"] * 20
# nums = ["82026", "02943N0", "362312", "00004254A2", "00006426YN", "00008120T7", "6270000290", "016409399B", "01М21С9"] * 20

df = pd.read_excel("file.xlsx")

df = df.apply(lambda col: col.astype(object))
df_to_list = df.values.tolist()
brands, nums = create(df_to_list)

brands_split = split_file_for_thr(8, brands)
nums_split = split_file_for_thr(8, nums)

threadings = []
for i in range(len(brands_split)):
    thread = threading.Thread(target=run, args=(brands_split[i], nums_split[i]), name=f"thr-{i}")
    thread.start()
    threadings.append(thread)

for thread in threadings:
    thread.join()

df = pd.DataFrame(all_data, columns=["Артикул", "Номер товара", "Лого", "Доставка", "Лучшая цена"])
df.to_excel("file(2).xlsx", index=False)

with open('data.txt', 'a', encoding="utf-8") as file:
    file.write(f"ВСЕГО: {total} строк\nБан лист: {ban_list}\nПопытки: {atms_proxy}\nСкорость: {total/(time.perf_counter() - start)} строк/секунд\nСтраница время: {(time.perf_counter() - start)/len(all_data)}\n{time.perf_counter() - start} секунд\n\n")