import random
import time
from datetime import datetime

from ENGINE import Parser
import requests
from bs4 import BeautifulSoup


class ParserFabrikant(Parser):

    def __init__(self, verify):
        super.__init__
        self.verify = verify
        self.url = "https://www.fabrikant.ru/trades/procedure/search/?type=1&org_type=org&currency=0&date_type=date_publication&ensure=all&filter_id=8&okpd2_embedded=1&okdp_embedded=1&count_on_page=10&order_direction=1&type_hash=1561441166"
        self.procedure_id = None
        self.response_item = None
        self.core = 'https://fabrikant.ru'
        self.monthlist = {
            "янв": 1,
            "фев": 2,
            "мар": 3,
            "апр": 4,
            "май": 5,
            "мая": 5,
            "июн": 6,
            "июл": 7,
            "авг": 8,
            "сен": 9,
            "окт": 10,
            "ноя": 11,
            "дек": 12,
            "янвр": 1,
            "февр": 2,
            "март": 3,
            "апрл": 4,
            "июнь": 6,
            "июль": 7,
            "авгс": 8,
            "сент": 9,
            "октб": 10,
            "нояб": 11,
            "дека": 12,
            "декаб": 12,
        }

    def parse(self):
        self.soup = self.get_page_soup(self.url)
        pagination = self.soup.find("ul", attrs={"class": "pagination__lt"}).find_all("li", attrs={"class": "pagination__lt__el"})
        last_page = pagination[-1].find("span").getText()
        #for page in range(1, 2):
        for page in range(1, int(last_page)+1):
            print(f'начали СТРАНИЦУ {page}')
            url = self.url + f'&page={page}'
            print('Суп страницы получен')
            page_soup = self.get_page_soup(url)
            print('Отправляем страницу на парсинг')
            offers = self.get_page_items(page_soup)
            for offer in offers:
                z = requests.post("https://synrate.ru/api/offers/create",
                                  json=offer)
                print(f'SEND {z}\n{offer}')
            time.sleep(random.randint(1, 7))
            print('Пауза')

    def get_page_soup(self, url):
        response = requests.get(url, headers={
            'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"},
                                     verify=self.verify).content.decode("utf8")
        soup = BeautifulSoup(response, 'html.parser')
        return soup

    def get_page_items(self, soup):
        items_divs = soup.find("section", attrs={"class":"marketplace-list"}).find_all("div", attrs={"class": "innerGrid"})
        print(f'Найдено: {len(items_divs)} заявок')
        offers = []
        for div in items_divs:
            # получаем данные из элементов
            link_element = div.find("h4", attrs={"class": "marketplace-unit__title"}).find("a")
            name, link = link_element.getText(), link_element.attrs['href']
            price = div.find("div", attrs={"class": "marketplace-unit__price"}).find("span").find("strong")
            date_divs = div.find("div", attrs={"class": "marketplace-unit__state__wrap"}).find_all("div", attrs={"class": "marketplace-unit__state"})
            company = div.find("div", attrs={"class": "marketplace-unit__organizer"}).find("a").find_all("span")[1].getText()
            company = company.replace('"', '')
            # отправляем данные в вспомогательные функции и приводим их в надлежащий вид
            answer = self.make_name_good(name)
            region = answer['region']
            text = answer['text']
            name = answer['name']

            link = self.core + link.replace(self.core, '')
            price = self.make_price_good(price)
            start_date, end_date = self.get_date(date_divs)

            # формируем словарь с данными по заявке и добавляем в список для ответа
            offer_obj = {"name": name,
                         "location": region, "home_name": "fabrikant",
                         #"offer_type": offer_type,
                         "offer_start_date": start_date, "offer_end_date": end_date,
                         "additional_data": text, "offer_price": price, "organisation": company,
                         "url": link#, "category": "Не определена", "subcategory": "не определена"
                         }
            offers.append(offer_obj)
            for key in offer_obj:
                print(f"{key}: {offer_obj[f'{key}']}")

        return offers

    def make_price_good(self, price):
        print(price)
        try:
            price = price.getText()
            print(price)
            price = price.replace(' ', '')
            price = int(price)
        except Exception as ex:
            print(ex)
            price = 0
        return price

    def get_date(self, date_divs):
        try:
            start_date = date_divs[0].find("span", attrs={"class": "dt"}).getText()
        except:
            start_date = None
        try:
            end_date = date_divs[1].find("span", attrs={"class": "dt"}).getText()
        except:
            end_date = None

        if start_date is not None:
            start_date = self.make_date_good(start_date)
        if end_date is not None:
            end_date = self.make_date_good(end_date)

        return start_date, end_date

    def make_name_good(self, name):
        answer = {}
        if 'Местоположение:' in name:
            print(f'регион в имени {name}')
            region = name.split('Местоположение:')[1]
            answer['region'] = region
            name = name.replace('Местоположение:', '').replace(region, '')
            print(f'make_name_good:\n{name}\n{region}')
        else:
            answer['region'] = ""

        name = name.split(' ')
        while '' in name:
            name.remove('')

        new_name = self.make_string(name)
        new_name = self.make_string(new_name.splitlines())

        answer['name'] = new_name

        if len(new_name) > 120:
            answer['text'] = new_name
        else:
            answer['text'] = ""

        return answer

    def make_string(self, line_list):
        new_line, i = '', 1
        for word in line_list:
            if i == 1:
                new_line += f'{word}'
            else:
                new_line += f" {word}"
            i += 1
        return new_line

    def make_date_good(self, date):
        date = date.split(' ')
        date = f'{date[2]}-{self.monthlist[f"{date[1]}"]}-{date[0]}'
        return date


if __name__ == '__main__':
    Parser = ParserFabrikant(True)
    Parser.parse()
