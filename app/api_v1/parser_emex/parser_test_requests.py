from fastapi import HTTPException, status

import asyncio
import json
import time
import random
import requests
import aiohttp
import httpx
import threading
import os
import aiofiles
import traceback

from fake_useragent import UserAgent

from typing import List

from app.core.config import settings
from app.core.models import NewFilter
from .depends import *

from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

user_data = {}
user_locks = {}


class ParserEmex:
    USERAGENTS = UserAgent()
    PROXIES = {
        "MANGO": {
            "http://": os.getenv("MANGOPROXY"),
            "https://": os.getenv("MANGOPROXY"),
        },
        "BRIGHTDATA": {
            "http://": os.getenv("BRIGHTDATAPROXY1"),
            "https://": os.getenv("BRIGHTDATAPROXY1"),
        },
    }
    TIMEOUTS = {
        "MANGO": (3, 5, 0.2),
        "BRIGHTDATA": (30, 35, 1.5),
    }
    SELECTELS = {
        "DATE": 1,
        "PRICE": 2,
    }
    PARSER_WORKER_STATUS = "PARSER_RUNNING"

    def __init__(self, _filter: NewFilter, status: str, brands: List, using_proxy: str, user_id: int):
        self.logo_srez = 10
        self.deep_filter = _filter.deep_filter
        self.deep_analog = _filter.deep_analog
        self.only_first_logo = _filter.only_first_logo
        self.analog = _filter.analog
        self.replacement = _filter.replacement
        self.is_bigger = _filter.is_bigger
        self.date = _filter.date
        self.logo = _filter.logo
        self.pickup_point = _filter.pickup_point
        self.columns = self.create_columns()
        self.status = status
        self.brands = brands
        self.browser = None
        self.all_break = None
        self.timeout1 = self.timeout2 = self.timeout3 = 0
        self.file_worker = FileWorker
        self.using_proxy = using_proxy
        self.path_to_save_file = os.path.join(settings.upload.path_for_upload, f"{user_id}_parsing.json")
        self.counter_parsered = 0
        self.checked_data = []
        self.headers = self.create_headers()

    def create_columns(self):
        columns = ["Код товара", "Артикул", "Наименование", "Брэнд", "Артикул", "Кол-во", "Цена", "Цена ABCP", "Партия", "Лого", "Доставка", "Лучшая цена", "Количество"]
        if self.logo:
            columns.append("Цена с лого")
        return columns
    
    def create_headers(self):
        useragent = self.USERAGENTS.random
        return {'User-Agent': useragent}

    def get_brand(self):
        return self.brands.pop(0)
    
    def back_brand(self, brand: List):
        self.brands.append(brand)
    
    def create_url(self, brand: List):
        return f"https://emex.ru/api/search/search?make={create_params_for_url(brand[3])}&detailNum={brand[1]}&locationId={self.pickup_point}&showAll=true&longitude=37.8613&latitude=55.7434"

    def get_proxy(self):
        return self.PROXIES[self.using_proxy]

    def get_timeouts(self):
        return self.TIMEOUTS[self.using_proxy]

    @staticmethod
    async def get_response(url: str, headers: dict, timeout: int, proxies: dict):
        async with httpx.AsyncClient(proxies=proxies, headers=headers, timeout=httpx.Timeout(read=timeout, pool=timeout, connect=timeout, write=timeout)) as client:
            response = await client.get(url)
            return response.json()

    def get_data_from_response(self, response: dict, _type: str):
        if _type == "ANALOG":
            goods_information = response["searchResult"][_type][:self.deep_analog]
        else:
            goods_information = response["searchResult"][_type]
        return [
            [
                good_field["offerKey"],
                int(
                    str(good_field["delivery"]["value"]).replace(
                        "Завтра", "1"
                    )
                ),
                good_field["displayPrice"]["value"],
                good_field["data"]["maxQuantity"]["value"],
            ]
            if self.check_date(good_field["delivery"]["value"]) else False
            for good_information in goods_information
            for good_field in good_information["offers"]
        ]
    
    def check_date(self, delivery):
        if self.is_bigger:
            return True if (self.date is None or int(str(delivery).replace("Завтра", "1")) >= self.date) else False
        else:
            return True if (self.date is None or int(str(delivery).replace("Завтра", "1")) <= self.date) else False

    def set_only_goods(self, goods):
        return [good for good in goods if good]

    def create_empty_result(self, brand):
        result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], brand[8], 0, 0, 0, 0,]
        if self.logo:
            result.append(0)
        return result

    async def saving_to_json(self, result):
        saving_to_json = {
            "good_code": result[0],
            "article": result[1],
            "name": result[2],
            "brand": result[3],
            "article1": result[4],
            "quantity": result[5],
            "price": result[6],
            "abcpprice": result[7],
            "batch": result[8],
            "logo": result[9],
            "delivery_time": result[10],
            "best_price": result[11],
            "quantity1": result[12]
        }
        if len(result) > 13: saving_to_json["new_price"] = result[13]
        await self.file_worker.rezerv_copy(self.path_to_save_file, saving_to_json)

    def get_sorted_data(self, goods):
        sorted_data_by_date = quick_sort(goods, self.SELECTELS["DATE"])
        cut_data_by_deep_filter = sorted_data_by_date[:self.deep_filter]
        sorted_by_price = quick_sort(cut_data_by_deep_filter, self.SELECTELS["PRICE"])
        return sorted_by_price

    def get_first_best_data(self, sorted_by_price):
        best_data = sorted_by_price[0]
        for idx in range(len(best_data)):
            try:
                best_data[idx] = int(best_data[idx])
            except:
                pass
        return best_data

    async def double_request(self, url, headers, timeout, proxies):
        try:
            response = await self.get_response(url=url, headers=headers, timeout=timeout, proxies=proxies)
        except:
            response = await self.get_response(url=url, headers=headers, timeout=timeout, proxies=proxies)
        return response

    async def algorithm_only_first_with_logo(self, sorted_by_price, brand, headers, timeout, timeout_between_response, proxies):
        first_second_goods = sorted_by_price[:2]
        price_with_logo = 0
        result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], brand[8], 0, 0, 0, 0, 0]
        for good in first_second_goods:
            url = f"https://emex.ru/api/search/rating?offerKey={good[0]}"
            while True:
                try:
                    response = await self.double_request(url=url, timeout=timeout, headers=headers, proxies=proxies)
                    break
                except httpx.TimeoutException as e:
                    traceback.print_exc()
            if response["priceLogo"] != self.logo:
                result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], brand[8], response["priceLogo"], *good[1:], price_with_logo]
                break
            else:
                price_with_logo = good[2]
            await asyncio.sleep(timeout_between_response)
        return result
    
    async def algorithm_get_best_about_good(self, best_data, brand, headers, timeout, proxies):
        url = f"https://emex.ru/api/search/rating?offerKey={best_data[0]}"
        response = await self.double_request(url=url, headers=headers, timeout=timeout, proxies=proxies)

        price_logo = response["priceLogo"]
        result = [brand[0], brand[1], brand[2], brand[3], brand[4], brand[5], brand[6], brand[7], brand[8], price_logo, *best_data[1:],]
        return result

    async def algorithm_get_price_with_logo(self, goods, brand, headers, timeout, proxies, timeout_between_response):
        best_data = None
        sorted_by_price = quick_sort(goods, self.SELECTELS["PRICE"])[:self.logo_srez]
        for data in sorted_by_price:
            url = f"https://emex.ru/api/search/rating?offerKey={data[0]}"
            response = await self.double_request(url=url, headers=headers, timeout=timeout, proxies=proxies)
            price_logo = response["priceLogo"]
            data[0] = price_logo
            if price_logo == self.logo:
                best_data = data
                break
            await asyncio.sleep(timeout_between_response)

        return best_data[2] if best_data else 0

    async def start_parser(self):
        while self.status == self.PARSER_WORKER_STATUS:
            timeout1, timeout2, timeout_between_response = self.get_timeouts()
            proxies = self.get_proxy()
            brand = self.get_brand()
            url = self.create_url(brand)

            try:
                response = await self.double_request(url=url, headers=headers, timeout=timeout, proxies=proxies) 
                goods = []
                if "originals" in response["searchResult"]:
                    goods += self.get_data_from_response(response=response, _type="originals")
                if self.replacement and "replacement" in response["searchResult"]:
                    goods += self.get_data_from_response(response=response, _type="replacement")
                if self.analog and "analog" in response["searchResult"]:
                    goods += self.get_data_from_response(response=response, _type="analog")

                if goods == []:
                    result = self.create_empty_result(brand)
                    self.counter_parsered += 1
                else:
                    goods = self.set_only_goods(goods)
                    sorted_by_price = self.get_sorted_data(goods)
                    if self.only_first_logo:
                        result = await self.algorithm_only_first_with_logo(sorted_by_price=sorted_by_price, brand=brand, headers=self.headers, timeout=timeout1, timeout_between_response=timeout_between_response, proxies=proxies)
                    else:
                        best_data = self.get_first_best_data(sorted_by_price=sorted_by_price)
                        result = await self.algorithm_get_best_about_good(best_data=best_data, brand=brand, headers=self.headers, timeout=timeout1, proxies=proxies)
                        if self.logo:
                            price_logo = await self.algorithm_get_price_with_logo(goods=goods, brand=brand, headers=self.headers, timeout=timeout2, proxies=proxies, timeout_between_response=timeout_between_response)
                            result.append(price_logo)

                await self.saving_to_json(result=result)
                self.checked_data.append(result)
            except Exception as e:
                self.back_brand(brand=brand)
                traceback.print_exc()

def run(parser: ParserEmex):
    asyncio.run(parser.start_parser())