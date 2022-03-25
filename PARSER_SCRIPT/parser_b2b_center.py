import random
import time
from datetime import datetime

from ENGINE import Parser
import requests
from bs4 import BeautifulSoup


class ParserCenter(Parser):

    def __init__(self, verify):
        super.__init__
        self.url = "https://www.b2b-center.ru/market/?searching=1&company_type=2&price_currency=0&date=1&trade=sell&lot_type=0"
        self.procedure_id = None
        self.response_item = None
        self.core = 'https://b2b-center.ru'
        self.core_www = 'https://www.b2b-center.ru'
        self.verify = verify

    def parse(self):
        # делаем запрос, получаем суп и отдаем функции, получающей номер последней страницы
        soup = self.get_page_soup(self.url)
        pagination = soup.find("div", attrs={"class": "pagi"}).find("ul", attrs={"class": "pagi-list"}).find_all("li", attrs={"class": "pagi-item"})
        last_page = pagination[-1].find("a").getText()
        # print(pagination)
        test = self.get_page_soup('https://www.b2b-center.ru/market/?searching=1&%3Bcompany_type=2&%3Bprice_currency=0&%3Bdate=1&%3Btrade=sell&%3Blot_type=0&from=20')
        test = test.find("div", attrs={"class": "inner"})
        print(test)




    def get_offers_from_page(self, soup):
        offers = soup.find("div", attrs={"class": "inner"})
        print(offers)
        answer = []
        for offer in offers:
            dates = offer.find_all("td", attrs={"class": "nowrap"})
            link = offer.find("a", attrs={"class": "search-results-title visited"}).attrs['href']
            name, text = offer.find("div", attrs={"class": "search-results-title-desc"}).getText().replace('"', '')
            company = offer.find("a", attrs={"class": "visited"}).getText().replace('"', '')

            start_date, end_date = self.get_dates(dates)
            link = self.core_www+link.replace(self.core, '').replace(self.core_www, '')
            offer_obj = {"name": name,
                         "home_name": "b2b-center",
                         "offer_start_date": start_date, "offer_end_date": end_date,
                         "additional_data": text, "organisation": company,
                         "url": link
                         }
            answer.append(offer_obj)
        return answer

    def get_dates(self, data):
        try:
            start_date = data[0].getText()
            start_date = start_date.split(' ')[0]
            start_date = start_date.split('.')
            day, month, year = start_date[0], start_date[1], start_date[2]
            start_date = f'{year}-{month}-{day}'
        except:
            start_date = None
        try:
            end_date = data[1].getText()
            end_date = end_date.split(' ')[0]
            end_date = end_date.split('.')
            day, month, year = end_date[0], end_date[1], end_date[2]
            end_date = f'{year}-{month}-{day}'
        except:
            end_date = None

        return start_date, end_date

    def get_page_soup(self, url):
        response = requests.get(url, headers={
            'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"},
                                     verify=self.verify).content.decode("utf8")
        soup = BeautifulSoup(response, 'html.parser')
        # print(response)
        return soup


if __name__ == '__main__':
    Parser = ParserCenter(True)
    Parser.parse()
