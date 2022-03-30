import random
import time

import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from ENGINE import Parser
from mixins import proxy_data, get_proxy


class ParserSource(Parser):
    def __init__(self):
        super().__init__()
        self.api_get_info_url = "https://reserve.isource.ru/api/auction/get-info"
        self.api_get_categories_url = "https://reserve.isource.ru/api/category/list/full"
        self.api_get_auction_url = "https://reserve.isource.ru/api/auction/list"
        self.response_item = None
        self.response_items = None
        self.response_categories = None
        self.proxy_mode = False

    def parse(self):
        successful = 0
        while not successful:
            try:
                self.response_categories = self.get_responce(self.api_get_categories_url, {"lvl": "1"}, self.proxy_mode)
                category_list = (self.response_categories["data"])
                successful = 1
            except:
                print(f'[isource] proxy_mode change. proxy_mode: {self.proxy_mode}')
                self.change_proxy()
        category_list.reverse()
        for category in category_list:
            successful = 0
            while not successful:
                try:
                    counter = 0
                    self.response_items = self.get_responce(self.api_get_auction_url, {
                                                            "category_name": category["transliteration_name"],
                                                            "page": 1,
                                                            "per_page": 100,}, self.proxy_mode)
                    test = self.response_items["data"]
                    successful = 1
                except:
                    print(f'[isource] proxy_mode change. proxy_mode: {self.proxy_mode}')
                    self.change_proxy()

            for z in self.response_items["data"]:
                successful = 0
                while not successful:
                    try:
                        self.response_item = self.get_responce(self.api_get_info_url, {"auction_transliteration_name": z
                                                           ["auction_transliteration_name"]}, self.proxy_mode)
                        self.response_item = self.response_item["data"]
                        successful = 1
                    except:
                        self.change_proxy()
                        print(f'[isource] proxy_mode change. proxy_mode: {self.proxy_mode}')

                if self.response_item["supplier_name"] != None:
                    organisation = self.response_item["supplier_name"]
                else:
                    organisation = ''
                J = {"name": self.response_item["name"].replace('"', ''),
                                        "location": self.response_item["region"][0]["name"],
                                        "home_name": "isource",
                                        "offer_type": "Продажа",
                                        "offer_start_date": self.response_item["date_begin"].split(" ")[0],
                                        "offer_end_date": self.response_item["date_end"].split(" ")[0],
                                        "owner": self.response_item["author_full_name"].replace('"', ''),
                                        "ownercontact": self.response_item["author_phone"],
                                        "offer_price": round(float(self.response_item["current_fix_price_without_nds"])),
                                        "additional_data": "не указано",
                                        "organisation": organisation.replace('"', ''),
                                        "url": "https://reserve.isource.ru/trades/item/"
                                               + self.response_item["auction_transliteration_name"]
                                        }
                z = requests.post("https://synrate.ru/api/offers/create",
                                  json=J)
                # TESTING -----------------
                try:
                    print(f'[isource] {z.json()}  {J}')
                except:
                    print(f'[isource] {z}  {J}')
                # time.sleep(random.randint(1, 5) / 10)
                # --------------------

    def get_responce(self, url, data, proxy_mode):
        if proxy_mode:
            successful = 0
            while not successful:
                proxy = get_proxy(proxy_mode)
                # proxy_status = check_proxy(proxy)
                try:
                    session = requests.Session()
                    retry = Retry(connect=3, backoff_factor=0.5)
                    adapter = HTTPAdapter(max_retries=retry)
                    session.mount('http://', adapter)
                    session.mount('https://', adapter)
                    response = session.post(url, headers={
                        'User-Agent': UserAgent().chrome}, data=data, proxies=proxy, timeout=5).json()
                    successful = 1
                except:
                    print(
                        '[isource] get_page_soup: не получилось сделать запрос с прокси. спим, меняем прокси и снова..')
                    self.change_proxy()
        else:
            response = requests.post(url, headers={
                'User-Agent': UserAgent().chrome}, data=data).json()
        return response

    def change_proxy(self):
        print('change_proxy: start')
        if self.proxy_mode:
            try:
                a = proxy_data[self.proxy_mode+1]
                self.proxy_mode += 1
                return True
            except:
                pass
        print(f'\n[isource] proxy_mode: {self.proxy_mode}')
        self.proxy_mode = 1
        return False


if __name__ == '__main__':
    parser = ParserSource()
    parser.parse()
