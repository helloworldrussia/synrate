import random
import time
from datetime import datetime

from django.conf import settings
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
        self.url = "https://onlinecontract.ru/sale?page={}"
        self.procedure_id = None
        self.response_item = None
        self.proxy_mode = False
        self.core = 'https://onlinecontract.ru'
        self.start_page = 50

    # def get_start_page(self):
    #     onlinecontract = Info.objects.get(name='onlinecontract')
    #     self.start_page = onlinecontract.start_page

    def parse(self):
        # self.get_start_page()
        successful = 0
        while not successful:
            time.sleep(random.randint(1, 15))
            try:
                last_page = self.get_last_page()
                successful = 1
            except Exception as ex:
                print(ex)
                self.change_proxy()

        for i in range(self.start_page, last_page+1):
            print(f'[onlinecontract] page = {i}')
            successful = 0
            while not successful:
                time.sleep(random.randint(1, 15))
                try:
                    soup = self.get_page_soup(self.url.format(i))
                    result = self.get_offers_from_page(soup)
                    if result:
                        self.send_result(result)
                        successful = 1
                except Exception as ex:
                    print(ex)
                    self.change_proxy()

    def get_last_page(self):
        soup = self.get_page_soup(self.url.format(1))
        last_page = soup.find("li", attrs={"class": "pagination-last page-item"}).find("a").attrs["href"]
        last_page = last_page.split('=')[-1]
        return int(last_page)

    def send_result(self, data):
        for offer in data:
            z = requests.post("https://synrate.ru/api/offers/create",
                              json=offer)
            today = datetime.today().strftime('%d-%m %H:%M')
            try:
                print(f'[onlinecontract] {z.json()}\n{offer}')
                # with open('/var/www/synrate_dir/onlinecontract.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z.json()}\n{offer}')
                #     f.close()
            except:
                print(f'[onlinecontract] {z}\n{offer}')
                # with open('/var/www/synrate_dir/onlinecontract.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z}\n{offer}')
                #     f.close()

    def get_offers_from_page(self, soup):
        try:
            offers = soup.find("tbody").find_all("tr")
            test = offers[1]
        except Exception as ex:
            print(ex)
            return False
        answer = []
        for offer in offers:
            parameters = offer.find_all("td")
            company = parameters[1].find("span").getText().replace('"', '')
            link_obj = parameters[2].find("a")
            link = self.core+link_obj.attrs['href']
            name = link_obj.find("span").getText().replace('"', '')
            end_date = parameters[3].getText()

            end_date = self.make_date_good(end_date)

            offer_obj = {"name": name, "home_name": "onlinecontract",
                                        "offer_end_date": end_date,
                                        "additional_data": name, "organisation": company, "url": link
                         }
            answer.append(offer_obj)
        return answer

    def make_date_good(self, date):
        by_points = date.split(".")
        year = '20' + by_points[-1].replace(' ', '')
        month = by_points[-2]
        day = by_points[-3].split(" ")[-1]
        date = f'{year}-{month}-{day}'
        return date

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
        if self.proxy_mode > 1:
            pass
            # time.sleep(300)
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
