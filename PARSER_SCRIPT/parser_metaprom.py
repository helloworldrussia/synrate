import math
import random
import sys
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import datetime
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from connector import change_parser_status, Item, DbManager
from ENGINE import Parser
from mixins import get_proxy


class ParserMetaprom(Parser):

    def __init__(self, verify, end):
        super().__init__()
        self.db_manager = DbManager()
        self.verify = verify
        self.url = "http://metaprom.ru"
        self.core = 'https://metaprom.ru'
        self.proxy = False
        self.current_proxy_ip = 0
        self.start_page = 1
        self.cat_list = []

    def parse(self):
        self.get_cat_list()
        self.category_disp()
        # change_parser_status('nelikvidy', 'Выкл')
        # sys.exit()

    def get_cat_list(self):
        soup = self.get_page_soup(self.url+'/board/')
        all = soup.find("div", attrs={"class": "rubrics"}).find_all("div", attrs={"class": "rubrics__group"})
        for cat in all:
            ul = cat.find("ul", attrs={"class": "rubrics__list"}).find_all("li")
            for li in ul:
                link = li.find("a").attrs['href']
                offers_count = li.find("span").getText().replace('(', '').replace(')', '')
                link = self.update_cat_url(self.url+link)
                self.cat_list.append({"url": link, "offers": int(offers_count)})

    def category_disp(self):
        if self.cat_list == []:
            raise ValueError("Неудалось собрать категории")
        for cat in self.cat_list:
            self.parse_cat(cat)

    def parse_cat(self, obj):
        pages_count = self.get_pages_count(obj)
        if pages_count == 0:
            return 0
        for page in range(0, pages_count):
            page_url = obj['url']+f'{page*50}'
            soup = self.get_page_soup(page_url)
            offers = self.get_offers_from_page(soup)
            self.send_result(offers)

    @staticmethod
    def get_pages_count(obj):
        if obj['offers'] == 0:
            return 0
        i, successful = 0, 0
        pages_count = math.ceil(obj['offers'] / 50)
        return pages_count

    @staticmethod
    def update_cat_url(url):
        cat_name = url.split('/')[-2]
        url = url.replace(f'{cat_name}/', f'?podrazdel={cat_name}&start=')
        return url

    def get_offers_from_page(self, soup):
        res = []
        offers = soup.find("table", attrs={"class": "maintable"}).find_all("tr")
        offers = self.check_trs(offers)
        for offer in offers:
            tds = offer.find_all("td")
            url = tds[0].find("a")
            name = tds[1].find("a")
            price = tds[1].find("span")
            start_date = tds[1].find_all("div")[-1]
            company = tds[2].find("a")
            region = tds[2].find("div")
            offer = self.validate(name, url, price, start_date, company, region)
            if offer:
                res.append(offer)

        return res

    def validate(self, name, url, price, start_date, company, region):
        if name:
            name = name.getText()
        else:
            return 0
        a_data = None
        if url:
            url = self.core+url.attrs['href']
            # a_data = self.get_a_data(url)
        if price:
            price = self.validate_price(price.getText())
        if start_date:
            start_date = self.validate_date(start_date.getText())
        if company:
            company = company.getText()
        if region:
            region = self.validate_region(region.getText())
            if region == 'na':
                return 0
        obj = Item(name, 'metaprom', url, region, start_date, None,
                None, None, price, a_data, company, None,
                None, None)

        return obj

    def get_a_data(self, url):
        soup = self.get_page_soup(url)
        try:
            main = soup.find("section", attrs={"class": "content"}).find_all("p")[1]
            a_data = main.getText()
        except:
            a_data = None
        return a_data

    @staticmethod
    def validate_region(region):
        if region.find(".") != -1:
            # print(region.split('.'))
            region = region.split('.')[0]
        if region == 'na':
            return 'na'
        return region

    @staticmethod
    def validate_date(date):
        date = date.split('.')
        date = f'{date[2]}-{date[1]}-{date[0]}'
        return date

    @staticmethod
    def validate_price(price):
        symbols = ['.', ',', '/', '-', '_', '₽', ' ', ':', '\\']
        if price == 'спрос':
            return None
        if price.find('от ') != -1:
            price = price.split('от ')[-1]
        price = ''.join(i for i in price if not i.isalpha())
        for symb in symbols:
            price = price.replace(symb, '')
        if price == '':
            return None
        price = price.replace(' ', '')
        return price

    @staticmethod
    def check_trs(data):
        checked = []
        for tr in data:
            try:
                style = tr.attrs['style']
                checked.append(tr)
            except:
                style = None
        return checked

    def send_result(self, result):
        for offer in result:
            offer.post(self.db_manager)
        self.db_manager.task_manager()

    def change_proxy(self):
        print('change_proxy: start')
        self.proxy, self.current_proxy_ip = get_proxy(self.current_proxy_ip)
        time.sleep(5)

    def get_page_soup(self, url):
        if self.current_proxy_ip:
            try:
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                response = session.get(url, headers={
                    'User-Agent': UserAgent().chrome}, proxies=self.proxy, timeout=5).content#.decode("utf8")
            except:
                print('[metaprom] get_page_soup: не получилось сделать запрос с прокси. спим, меняем прокси и снова..')
                return False
        else:
            response = requests.get(url, headers={
                'User-Agent': UserAgent().chrome}).content#.decode("utf8")
        soup = BeautifulSoup(response, 'html.parser')
        # print(response)
        return soup


if __name__ == '__main__':
    parser = ParserMetaprom(False, False)
    parser.parse()
