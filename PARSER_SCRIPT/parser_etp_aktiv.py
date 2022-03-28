import random
import time
from datetime import datetime

from fake_useragent import UserAgent

from ENGINE import Parser
import requests
from bs4 import BeautifulSoup


class ParserEtpActiv(Parser):

    def __init__(self, verify):
        super.__init__
        self.verify = verify
        self.url = "https://etp-aktiv.ru/catalog/"
        self.procedure_id = None
        self.response_item = None
        self.core = 'https://etp-aktiv.ru'
        self.core_www = 'https://www.etp-aktiv.ru'

    def parse(self):
        last_page = self.get_last_page()
        for page in range(1, last_page+1):
            page_url = self.url+f'?PAGEN_1={page}'
            result = self.get_page_offers(page_url)
            self.post_result(result)
            print(f'etp-activ: Обрабатываем страницу - {page_url}')
            time.sleep(random.randint(1, 10))

    def get_page_soup(self, url):
        response = requests.get(url, headers={
            'User-Agent': UserAgent().chrome},
                                verify=self.verify).content.decode("utf8")
        soup = BeautifulSoup(response, 'html.parser')
        # print(response)
        return soup

    def get_last_page(self):
        soup = self.get_page_soup(self.url)
        last_page = soup.find("nav", attrs={"class": "nav nav--pager"}).find("ul")
        last_page = last_page.find_all("li", attrs={"class": "nav__item"})[-2].find("a").getText()
        last_page.replace('\n', '').replace(' ', '')
        return int(last_page)

    def get_page_offers(self, url):
        soup = self.get_page_soup(url)
        offers = soup.find("div", attrs={"class": "products-cards"}).find_all("div", attrs={"class": "products-cards__item"})
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
            print(f'etp-activ: {z}\n{offer}')


if __name__ == '__main__':
    Parser = ParserEtpActiv(True)
    Parser.parse()
