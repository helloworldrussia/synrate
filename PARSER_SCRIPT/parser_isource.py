import sys
import time
from datetime import datetime
import requests
from connector import change_parser_status, Item
from ENGINE import Parser


class ParserSource(Parser):
    def __init__(self, end):
        super().__init__()
        self.api_get_info_url = "https://reserve.isource.ru/api/auction/get-info"
        self.api_get_categories_url = "https://reserve.isource.ru/api/category/list/full"
        self.api_get_auction_url = "https://reserve.isource.ru/api/auction/list"
        self.response_item = None
        self.response_items = None
        self.response_categories = None
        self.current_proxy_ip = 0
        self.proxy = False
        self.count = 0
        self.last_page = end

    def get_last_page(self):
        response = requests.post(self.api_get_auction_url, headers={
            'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"},
                                            data={
                                                # "category_name": category["transliteration_name"],
                                                "page": 1,
                                                "per_page": 100}).json()
        last_page = response['pagination']['page_count']
        return int(last_page)

    def parse(self):
        last_page = self.get_last_page()
        if self.last_page:
            last_page = int(self.last_page)
        for i in range(1, last_page+1):
            i += 1
            time.sleep(15)
            print('next PAGE')
            counter = 0
            self.response_items = requests.post(self.api_get_auction_url, headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"},
                                                data={
                                                    #"category_name": category["transliteration_name"],
                                                    "page": i,
                                                    "per_page": 100,

                                                }).json()
            for z in self.response_items["data"]:
                self.response_item = requests.post(self.api_get_info_url, headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"},
                                                   data={"auction_transliteration_name": z["auction_transliteration_name"]}).json()["data"]
                # print(self.response_item)
                offer = {"name": self.response_item["name"],
                                        "location": self.response_item["region"][0]["name"],
                                        "home_name": "isource",
                                        "offer_type": "Продажа",
                                        "offer_start_date": self.response_item["date_begin"].split(" ")[0],
                                        "offer_end_date": self.response_item["date_end"].split(" ")[0],
                                        "owner": self.response_item["author_full_name"],
                                        "ownercontact": self.response_item["author_phone"],
                                        "offer_price": round(float(self.response_item["current_price_with_nds"])),
                                        "additional_data": "не указано",
                                        "organisation": self.response_item["contragent_host_name"],
                                        "url": "https://reserve.isource.ru/trades/item/"
                                               + self.response_item["auction_transliteration_name"],
                                        "from_id": self.response_item['auction_transliteration_name'].split("-")[-1]
                                        }
                offer = Item(self.response_item["name"], "isource",
                    "https://reserve.isource.ru/trades/item/"+self.response_item["auction_transliteration_name"],
                    self.response_item["region"][0]["name"],
                    self.response_item["date_begin"].split(" ")[0], self.response_item["date_end"].split(" ")[0],
                    self.response_item["author_full_name"], self.response_item["author_phone"],
                    round(float(self.response_item["current_price_with_nds"])),
                    None, self.response_item["contragent_host_name"], self.response_item['auction_transliteration_name'].split("-")[-1],
                    None, None)
                offer.post()
        change_parser_status('isource', 'Выкл')
        sys.exit()


if __name__ == '__main__':
    parser = ParserSource(False)
    parser.parse()