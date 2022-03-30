import random
import time
from datetime import datetime

from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter, Retry

from ENGINE import Parser
import requests
from bs4 import BeautifulSoup

from mixins import get_proxy, proxy_data


class ParserEtpActiv(Parser):

    def __init__(self, verify):
        super.__init__
        self.verify = verify
        self.url = "https://etp-aktiv.ru/catalog/"
        self.procedure_id = None
        self.response_item = None
        self.core = 'https://etp-aktiv.ru'
        self.core_www = 'https://www.etp-aktiv.ru'
        self.proxy_mode = False

    def parse(self):
        last_page = self.get_last_page()
        for page in range(1, int(last_page)+1):
            time.sleep(random.randint(1, 7))
            successful = 0
            while not successful:
                time.sleep(random.randint(1, 7))
                page_url = self.url+f'?PAGEN_1={page}'
                result = self.get_page_offers(page_url)
                if result:
                    successful = 1
                self.post_result(result)
                print(f'etp-activ: Обрабатываем страницу - {page_url}\nproxy_mode: {self.proxy_mode}')
            # time.sleep(random.randint(1, 3))

    def get_page_soup(self, url, proxy_mode):
        if proxy_mode:
            proxy = get_proxy(proxy_mode)
            # proxy_status = check_proxy(proxy)
            try:
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                response = session.get(url, headers={
                    'User-Agent': UserAgent().chrome}, proxies=proxy, timeout=5).content.decode("utf8")
                soup = BeautifulSoup(response, 'html.parser')
            except:
                print('get_page_soup: не получилось сделать запрос с прокси. спим, меняем прокси и снова..')
                return False
        else:
            response = requests.get(url, headers={
                'User-Agent': UserAgent().chrome},
                                    verify=self.verify).content.decode("utf8")
        soup = BeautifulSoup(response, 'html.parser')
        # print(response)
        return soup

    def get_last_page(self):
        successful = 0
        while not successful:
            try:
                soup = self.get_page_soup(self.url, self.proxy_mode)
                last_page = soup.find("nav", attrs={"class": "nav nav--pager"}).find("ul")
                last_page = last_page.find_all("li", attrs={"class": "nav__item"})[-2].find("a").getText()
                last_page.replace('\n', '').replace(' ', '')
                int(last_page)
                successful = 1
            except:
                self.change_proxy()
        return last_page

    def change_proxy(self):
        print('change_proxy: start')
        if self.proxy_mode:
            try:
                a = proxy_data[self.proxy_mode+1]
                self.proxy_mode += 1
                return True
            except:
                pass
        print(f'\nproxy_mode: {self.proxy_mode}')
        self.proxy_mode = 1
        if self.proxy_mode > 1:
            time.sleep(300)
        return False

    def get_page_offers(self, url):

        soup = self.get_page_soup(url, self.proxy_mode)
        try:
            offers = soup.find("div", attrs={"class": "products-cards"}).find_all("div", attrs={"class": "products-cards__item"})
        except:
            self.change_proxy()
            return False

        print(len(offers))
        answer = []
        for offer in offers:
            link_obj = offer.find("div", attrs={"class": "product-card__header"}).find("a", attrs={"class": "product-card__header-img"})
            region = offer.find("span", attrs={"class": "product-card__descr-row"})
            region = region.find("span", attrs={"class": "product-card__descr-row__value"})

            name = link_obj.find("img").attrs['alt'].replace('"', '')
            text = name
            link = self.core+link_obj.attrs['href']

            offer_obj = {"name": name,
                 "home_name": "etp-activ",
                 #"offer_start_date": start_date, "offer_end_date": end_date,
                 "additional_data": text,# "organisation": company,
                 "url": link
                         }
            if region is not None:
                offer_obj['location'] = region.getText().replace('\n', '').replace(' ', '')
            else:
                region = None

            answer.append(offer_obj)
        return answer

    def post_result(self, data):
        for offer in data:
            z = requests.post("https://synrate.ru/api/offers/create",
                              json=offer)
            try:
                print(f'[etp-aktiv] {z.json()}\n{offer}')
            except:
                print(f'[etp-aktiv] {z}\n{offer}')


if __name__ == '__main__':
    Parser = ParserEtpActiv(True)
    Parser.parse()
