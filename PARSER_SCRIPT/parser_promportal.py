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


class ParserPromportal(Parser):

    def __init__(self, verify, end):
        super().__init__()
        self.db_manager = DbManager()
        self.verify = verify
        self.url = "https://promportal.su/g/"
        self.core = 'https://promportal.su'
        self.proxy = False
        self.current_proxy_ip = 0
        self.start_page = 1
        self.cat_list = []
        self.target_urls = []
        self.current_category = None
        self.last_page = end

    def parse(self):
        successful = 0
        while not successful:
            try:
                self.get_cat_list()
                if self.cat_list != []:
                    successful = 1
                else:
                    self.change_proxy()
                    time.sleep(3)
            except:
                self.change_proxy()
                time.sleep(3)
        # delete this line after debug
        l = len(self.cat_list)
        del self.cat_list[int(l/4):int(l/2)]
        print('Good. We get it.', len(self.cat_list))
        self.categories_scanner()

    def categories_scanner(self):
        while self.cat_list != []:
            for cat in self.cat_list:
                successful = 0
                while not successful:
                    try:
                        print('checking', cat)
                        if self.check_page_content_type(cat):
                            print('good. good list:', len(self.target_urls))
                            # self.target_urls.append(cat)
                            self.cat_list.remove(cat)
                            self.scanner(cat)
                        else:
                            print('bad. cat list:', len(self.cat_list))
                            self.scan_sub_in_cat(cat)
                        successful = 1
                    except:
                        pass

        change_parser_status('promportal', 'Выкл')
        sys.exit()

    def scan_sub_in_cat(self, obj):
        self.cat_list.remove(obj)
        soup = self.get_page_soup(obj['url'])
        current_name = obj['cat'].split('/')[0]
        ul = soup.find("ul", attrs={"class": "category-gallery-items"}).find_all("li")
        for li in ul:

            try:
                a_all = li.find("div", attrs={"class": "tags"}).find_all("a")
            except:
                a = li.find("div", attrs={"class": "name"}).find("a")
                subcat_name, link = f'{current_name}/'+a.getText(), a.attrs['href']
                self.cat_list.append({"url": link, "cat": f"{current_name}"})

            for a in a_all:
                subcat_name = a.getText()
                link = a.attrs['href']
                if subcat_name != 'Смотреть все':
                    current_name += f'/{subcat_name}'
                    self.cat_list.append({"url": link, "cat": f"{current_name}"})

    def check_page_content_type(self, obj):
        url = obj['url']
        soup = self.get_page_soup(url)
        try:
            offers = soup.find("div", attrs={"class": "gallery-block"}).find_all("div", attrs={"class": "gb-item"})
            return True
        except:
            return False

    def scanner(self, cat_object):
        successful = 0
        while not successful:
            try:
                last_page = self.get_last_page(cat_object['url'])
                successful = 1
            except:
                self.change_proxy()
        if self.last_page:
            if last_page > self.last_page: pages_count = self.last_page
        for page in range(1, last_page+1):
            successful = 0
            while not successful:
                try:
                    page_url = cat_object['url']+f'?page={page}'
                    print(page_url)
                    soup = self.get_page_soup(page_url)
                    offers = self.get_offers_from_page(soup, cat_object['cat'])
                    successful = 1
                    if offers:
                        self.send_result(offers)
                except:
                    self.change_proxy()
    def get_offers_from_page(self, soup, category):
        res = []
        offers = soup.find("div", attrs={"class": "gallery-block"}).find_all("div", attrs={"class": "gb-item"})
        for offer in offers:
            core = offer.find("div", attrs={"class": "gbi-info"})
            try:
                a = core.find("div", attrs={"class": "gbic-name"}).find("a")
            except:
                continue
            price = core.find("div", attrs={"class": "gbic-price"}).getText()
            company = self.validate_company(core.find("div", attrs={"class": "gbic-firm-name"}))
            region = core.find("div", attrs={"class": "gbic-firm-city"}).getText()

            name = a.find("span").getText()
            url = a.attrs['href']

            url = url.replace(' ', '')

            if price:
                price = self.validate_price(price.replace(' ', ''))
            if company:
                company = company.replace('"', '').replace("'", '')

            offer = Item(name, 'promportal', url, region, None, None,
                None, None, price, None, company, None,
                category, None)
            res.append(offer)
        return res

    def get_last_page(self, url):
        try:
            soup = self.get_page_soup(url)
            a = soup.find('div', attrs={"class": "pager"}).find_all("a")[-2]
            last_page = int(a.getText())
        except:
            last_page = 1
        return last_page

    def get_cat_list(self):
        soup = self.get_page_soup(self.url)
        all = soup.find("ul", attrs={"class": "category c-goods"}).find_all("li")
        i = 0
        cat_list = []
        for cat in all:
            try:
                cat_name = cat.find("a").getText()
                ul = cat.find("ul").find_all('li')
                i += 1
            except:
                continue

            for li in ul:
                a = li.find("a")
                link, subcat_name = a.attrs['href'], a.getText()
                self.cat_list.append({"url": link, "cat": f"{cat_name}/{subcat_name}"})

    @staticmethod
    def validate_company(data):
        try:
            data = data.find("a").getText()
        except:
            try:
                data = data.find("span").getText()
            except:
                data = None
        if data is not None:
            data = data.split(' ')
            while '' in data: data.remove('')
            while '\n' in data: data.remove('\n')
            text, i = '', 0
            for word in data:
                if i:
                    text += f' {word}'
                else:
                    text = word
                i += 1
            data = text
        return data

    @staticmethod
    def validate_price(price):
        symbols = ['.', ',', '/', '-', '_', '₽', ' ', ':', '\\']
        price = ''.join(i for i in price if not i.isalpha())
        for symb in symbols:
            price = price.replace(symb, '')
        price = price.replace(' ', '').replace(' ', '')
        if price == '':
            return None
        return price

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
                print('[promportal] get_page_soup: не получилось сделать запрос с прокси. спим, меняем прокси и снова..')
                return False
        else:
            response = requests.get(url, headers={
                'User-Agent': UserAgent().chrome}).content#.decode("utf8")
        soup = BeautifulSoup(response, 'html.parser')
        # print(response)
        return soup


if __name__ == '__main__':
    parser = ParserPromportal(False, False)
    parser.parse()
