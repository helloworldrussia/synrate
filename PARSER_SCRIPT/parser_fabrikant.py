import random
import time
from datetime import datetime
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter, Retry
from connector import change_parser_status, Item
from ENGINE import Parser
import requests
from bs4 import BeautifulSoup
from mixins import proxy_data, get_proxy
import sys


class ParserFabrikant(Parser):

    def __init__(self, verify, end):
        super.__init__
        self.verify = verify
        self.url = "https://www.fabrikant.ru/trades/procedure/search/?type=1&org_type=org&currency=0&date_type=date_publication&ensure=all&filter_id=8&okpd2_embedded=1&okdp_embedded=1&count_on_page=10&order_direction=1&type_hash=1561441166"
        self.procedure_id = None
        self.response_item = None
        self.core = 'https://fabrikant.ru'
        self.core_www = 'https://www.fabrikant.ru'
        self.proxy = False
        self.current_proxy_ip = 0
        self.last_page = end
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
        last_page = self.get_last_page()
        if self.last_page:
            last_page = int(self.last_page)
        for page in range(1, int(last_page)+1):
            time.sleep(random.randint(5, 10))
            successful = 0
            while not successful:
                time.sleep(random.randint(1, 7))
                print(f'fabrikant: Сканируем стр. {page}\nproxy_mode: {self.current_proxy_ip}')
                page_soup = self.get_page_soup(self.url + f'&page={page}')
                offers = self.get_page_items(page_soup)
                if offers:
                    successful = 1

            for offer in offers:
                offer.post()
        change_parser_status('fabrikant', 'Выкл')
        sys.exit()

    def get_last_page(self):
        successful = 0
        while not successful:
            soup = self.get_page_soup(self.url)
            try:
                pagination = soup.find("ul", attrs={"class": "pagination__lt"}).find_all("li", attrs={
                    "class": "pagination__lt__el"})
                last_page = pagination[-1].find("span").getText()
                successful = 1
            except:
                self.change_proxy()

        return last_page

    def change_proxy(self):
        print('change_proxy: start')
        self.proxy, self.current_proxy_ip = get_proxy(self.current_proxy_ip)
        time.sleep(30)

    def get_page_soup(self, url):
        if self.current_proxy_ip:
            try:
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                response = session.get(url, headers={
                    'User-Agent': UserAgent().chrome}, proxies=self.proxy, timeout=5).content.decode("utf8")
            except:
                print('[fabrikant] get_page_soup: не получилось сделать запрос с прокси. спим, меняем прокси и снова..')
                return False
        else:
            response = requests.get(url, headers={
                'User-Agent': UserAgent().chrome}).content.decode("utf8")
        soup = BeautifulSoup(response, 'html.parser')
        return soup

    def get_page_items(self, soup):
        try:
            items_divs = soup.find("section", attrs={"class": "marketplace-list"}).find_all("div", attrs={"class": "innerGrid"})
        except:
            self.change_proxy()
            return False
        offers = []
        for div in items_divs:
            # получаем данные из элементов
            from_id = div.find("div", attrs={"class": "marketplace-unit__info"}).find("div", attrs={"class": "marketplace-unit__info__name"})
            link_element = div.find("h4", attrs={"class": "marketplace-unit__title"}).find("a")
            name, link = link_element.getText(), link_element.attrs['href']
            price = div.find("div", attrs={"class": "marketplace-unit__price"}).find("span").find("strong")
            date_divs = div.find("div", attrs={"class": "marketplace-unit__state__wrap"}).find_all("div", attrs={"class": "marketplace-unit__state"})
            company = div.find("div", attrs={"class": "marketplace-unit__organizer"}).find("a").find_all("span")[1].getText()
            company = company.replace('"', '')
            from_id = from_id.find("span").getText()
            from_id = from_id.split('№')[-1].replace(' ', '').replace('\n', '')
            # отправляем данные в вспомогательные функции и приводим их в надлежащий вид
            answer = self.make_name_good(name)
            region = answer['region']
            text = answer['text']
            name = answer['name']

            link = self.core + link.replace(self.core, '').replace(self.core_www, '')
            price = self.make_price_good(price)
            start_date, end_date = self.get_date(date_divs)

            # формируем словарь с данными по заявке и добавляем в список для ответа
            offer_obj = {"name": name,
                         "location": region, "home_name": "fabrikant",
                         #"offer_type": offer_type,
                         "offer_start_date": start_date, "offer_end_date": end_date,
                         "additional_data": text, "offer_price": price, "organisation": company,
                         "url": link, "from_id": from_id
                         }
            offer = Item(name, "fabrikant", link, region, start_date, end_date,
                None, None, price, text, company, from_id,
                None, None)
            offers.append(offer)

        return offers

    def make_price_good(self, price):
        try:
            price = price.getText()
            price = price.replace(' ', '')
            price = int(price)
        except Exception as ex:
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
            region = name.split('Местоположение:')[1]
            answer['region'] = region
            name = name.replace('Местоположение:', '').replace(region, '')
        else:
            answer['region'] = ""

        name = name.split(' ')
        while '' in name:
            name.remove('')

        new_name = self.make_string(name)
        new_name = self.make_string(new_name.splitlines())

        answer['name'] = new_name
        answer['text'] = new_name

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
    Parser = ParserFabrikant(True, False)
    Parser.parse()
