import random
import time
from datetime import datetime

from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from ENGINE import Parser
import requests
from bs4 import BeautifulSoup

from mixins import get_proxy, proxy_data


class ParserOnlineContract(Parser):
    def __init__(self):
        super.__init__
        self.url = "https://onlinecontract.ru/sale?limit=100&page={}"
        self.procedure_id = None
        self.response_item = None
        self.proxy_mode = 3

    def parse(self):
        for i in range(1, 50):
            print(i)
            # self.response = requests.get(self.url.format(i), headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"}, verify=False).content. \
            #     decode("utf8")
            # self.soup = BeautifulSoup(self.response, 'html.parser')
            successful = 0
            while not successful:
                print(333)
                try:
                    self.soup = self.get_page_soup(self.url.format(i))
                    print(111)
                    self.post_links = self.soup.find_all("a", attrs={"class": "g-color-black"})
                    print(222)
                    test = self.post_links[0]
                    self.post_links = list(set(self.post_links))
                    successful = 1
                except:
                    self.change_proxy()
                    print(f'[online] new proxy_mode {self.proxy_mode}')

            self.post_links.reverse()
            print('[online] перевернули post_links')
            for post in self.post_links:
                print(f'[online] {post}')
                self.procedure_id = post["href"].split("/")[2].split("?")[0]
                successful = 0
                while not successful:
                    try:
                        if self.proxy_mode:
                            proxy = get_proxy(self.proxy_mode)
                            self.response_item = requests.get(
                                "https://api.onlc.ru/purchases/v1/public/procedures/{}/positions".format(self.procedure_id),
                                headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"},
                            proxies=proxy, timeout=5).json()["data"][0]
                            successful = 1
                        else:
                            self.response_item = requests.get(
                                "https://api.onlc.ru/purchases/v1/public/procedures/{}/positions".format(self.procedure_id),
                                headers={
                                    'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"},
                                proxies=proxy, timeout=5).json()["data"][0]
                            successful = 1
                    except:
                        self.change_proxy()
                        print(f'[online] new proxy_mode {self.proxy_mode}')

                try:
                    date = self.response_item["OwnerSklad"].split(".")[2] + "-" + self.response_item["OwnerSklad"].split(".")[1] + "-" + self.response_item["OwnerSklad"].split(".")[0]

                    datetime.strptime(date, "%Y-%m-%d")
                except:
                    date = None
                null = None
                J = {"name": self.response_item["Name"].replace('"', ''),
                                        "location": "",
                                        "home_name": "onlinecontract",
                                        "offer_type": "Продажа",
                                        "offer_start_date": null,
                                        "offer_end_date": date,
                                        "owner": "",
                                        "ownercontact": "",
                                        "offer_price": int(float(self.response_item["Price"])),
                                        "additional_data": self.response_item["OwnerCondi"],
                                        "organisation": "",
                                        "url": f"https://onlinecontract.ru/tenders/{self.response_item['IDA']}"
                                        #"category": "Не определена", "subcategory": "не определена"
                                        }
                z = requests.post("https://synrate.ru/api/offers/create",
                                  json=J)
                # TESTING -------------
                try:
                  print(f'[online] {z.json()}  {J}')
                except Exception as ex:
                  print(f'[online] {z}  {J}')
                time.sleep(random.randint(1, 5) / 10)
                # ---------------------

    def change_proxy(self):
        print('[online] change_proxy: start')
        if self.proxy_mode:
            try:
                a = proxy_data[self.proxy_mode+1]
                self.proxy_mode += 1
                return True
            except:
                pass
        print(f'\n[online] proxy_mode: {self.proxy_mode}')
        self.proxy_mode = 1
        return False

    def get_page_soup(self, url):
        if self.proxy_mode:
            proxy = get_proxy(self.proxy_mode)
            # proxy_status = check_proxy(proxy)
            try:
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                response = session.get(url, headers={
                    'User-Agent': UserAgent().chrome}, proxies=proxy, timeout=5).content.decode("utf8")
            except:
                print('[online] get_page_soup: не получилось сделать запрос с прокси. спим, меняем прокси и снова..')
                return False
        else:
            response = requests.get(url, headers={
                'User-Agent': UserAgent().chrome}).content.decode("utf8")
        print(response)
        soup = BeautifulSoup(response, 'html.parser')
        return soup


if __name__ == '__main__':
    Parser = ParserOnlineContract()
    Parser.parse()
