import random
import time

import requests
from ENGINE import Parser


class ParserSource(Parser):
    def __init__(self):
        super().__init__()
        self.api_get_info_url = "https://reserve.isource.ru/api/auction/get-info"
        self.api_get_categories_url = "https://reserve.isource.ru/api/category/list/full"
        self.api_get_auction_url = "https://reserve.isource.ru/api/auction/list"
        self.response_item = None
        self.response_items = None
        self.response_categories = None

    def parse(self):

        self.response_categories = requests.post(self.api_get_categories_url, headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"}
                                                 , data={"lvl": "1"}).json()
        category_list = (self.response_categories["data"])
        for category in category_list:
            counter = 0
            self.response_items = requests.post(self.api_get_auction_url, headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"},
                                                data={
                                                    "category_name": category["transliteration_name"],
                                                    "page": 1,
                                                    "per_page": 100,

                                                }).json()
            for z in self.response_items["data"]:
                self.response_item = requests.post(self.api_get_info_url, headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"},
                                                   data={"auction_transliteration_name": z
                                                   ["auction_transliteration_name"]}).json()["data"]

                if self.response_item["supplier_name"] != None:
                    organisation = self.response_item["supplier_name"]
                else:
                    organisation = ''
                z = requests.post("https://synrate.ru/api/offers/create",
                                  json={"name": self.response_item["name"].replace('"', ''),
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
                                               + self.response_item["auction_transliteration_name"],
                                        "category": category["transliteration_name"],
                                        "subcategory": self.response_item["category"][0]["name"]
                                        }
                                  )

                try:
                    if z.json()["name"][0].find("already exists") != -1:
                        counter += 1

                        if counter == 150:
                            break
                except:
                    counter = 0
                    z = None
                # TESTING -----------------

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
                                               + self.response_item["auction_transliteration_name"],
                                        "category": category["transliteration_name"],
                                        "subcategory": self.response_item["category"][0]["name"]
                                        }
                try:
                    print(f'Isource: {z.json()}  {J}')
                except:
                    print(f'Isource !!!!: {z}  {J}')
                time.sleep(random.randint(1, 5) / 10)
                # --------------------


if __name__ == '__main__':
    parser = ParserSource()
    parser.parse()
