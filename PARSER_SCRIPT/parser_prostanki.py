import sys
import threading

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from connector import change_parser_status, Item
from ENGINE import Parser
import time
import random
import datetime
from mixins import proxy_data, get_proxy


class ProstankiParser(Parser):
    def __init__(self, end):
        super().__init__()
        self.url = 'https://www.prostanki.com/'
        self.proxy = False
        self.current_proxy_ip = 0
        self.start_page = 1
        self.last_page = end
        self.target_list = []
        self.cur_cat = None

    def get_target_url(self):
        successful = 0
        while not successful:
            try:
                soup = self.get_page_soup(self.url)
                cat = soup.find_all("div", attrs={"class": "panel b-category-tree-block"})
                for item in cat:
                    # all = item.find("ul", attrs={"class": "childs"})
                    all = item.find_all("li")
                    for x in all:
                        x = x.find("a")
                        url = x.attrs['href']
                        self.target_list.append(url)
                    successful = 1
            except:
                self.change_proxy()

    def parse(self):
        self.get_target_url()
        for cat in self.target_list:
            self.cur_cat = cat
            self.parse_cat(cat)
        change_parser_status('prostanki', 'Выкл')
        sys.exit()

    def parse_cat(self, url):
        last_page = self.get_last_page(url)
        for page in range(1, last_page+1):
            successful = 0
            while not successful:
                try:
                    page_url = url+f'/{page}'
                    page_soup = self.get_page_soup(page_url)
                    result = self.get_offers_from_page(page_soup)
                    if result:
                        th = threading.Thread(target=self.post, args=(result,))
                        th.start()
                    successful = 1
                except:
                    self.change_proxy()

    def get_offers_from_page(self, soup):
        offers = soup.find_all("div", attrs={"class": "b-item-block-box"})
        answer = []
        for offer in offers:
            try:
                # проверяем спонсорское ли это объявление (только они имеют такой атрибут)
                # пропускаем такие объявы
                test = offer.find("a", attrs={"rel": "sponsored"}).attrs['href']
                continue
            except:
                pass
            a = offer.find("a", attrs={"class": "b-title"})
            url, name = a.attrs['href'], a.getText()
            try:
                company = offer.find("div", attrs={"class": "b-company"}).getText().replace('"', '')
            except:
                company = None
            start_date = offer.find("span", attrs={"class": "b-date"}).find("span").getText()
            try:
                a_data = offer.find("div", attrs={"class": "b-description"}).find("small").getText()
            except:
                a_data = None
            price = offer.find("div", attrs={"class": "b-price"}).getText().replace(' ', '')
            region = offer.find("span", attrs={"class": "b-geo"}).getText()

            splt = start_date.split('.')
            start_date = f'{splt[-1]}-{splt[-2]}-{splt[-3]}'
            try:
                price = int(price)
            except:
                price = None

            item = Item(name, 'prostanki', url, region, start_date, None,
                None, None, price, a_data, company, None,
                None, None)
            answer.append(item)

        return answer

    def get_last_page(self, url):
        try:
            soup = self.get_page_soup(url)
            last_page = soup.find("ul", attrs={"class": "pagination"}).find_all("li")[-2].find("a").getText()
            last_page = int(last_page)
        except:
            last_page = 1
        return last_page

    def get_page_soup(self, url):
        if self.current_proxy_ip:
            try:
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                response = session.get(url, headers={
                    'User-Agent': UserAgent().chrome}, proxies=self.proxy, timeout=5)#.content.decode("utf8")
                response.encoding = 'utf-8'
                response = response.content
            except Exception as ex:
                print('get_page_soup: не получилось сделать запрос с прокси. спим, меняем прокси и снова..',
                      f'\n{url}\n\n{ex}')
                time.sleep(2)
                return False
        else:
            response = requests.get(url, headers={
                'User-Agent': UserAgent().chrome}).content.decode("utf8")
        soup = BeautifulSoup(response, 'html.parser')
        # print(response)
        return soup

    def change_proxy(self):
        print(f'cur_cat = {self.cur_cat}\nchange_proxy: start')
        self.proxy, self.current_proxy_ip = get_proxy(self.current_proxy_ip)
        time.sleep(15)

    def post(self, result):
        for x in result:
            x.post()


if __name__ == '__main__':
    parser = ProstankiParser(False)
    parser.parse()
