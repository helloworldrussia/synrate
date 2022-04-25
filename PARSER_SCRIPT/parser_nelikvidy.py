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


class ParserNelikvidy(Parser):

    """
        Главный класс парсера сайта nelikvidi.com .
    """

    def __init__(self, verify, end):
        """
            Наследованный класс парсера. Добавленное поле verify нужно потому что у сайта сертификат протух,
             поэтому verify нужно поставить на False. Потом при необходимости не проблема вернуть обратно.
        :param verify:
        """
        super().__init__()
        self.db_manager = DbManager()
        self.verify = verify
        self.last_page = end
        self.url = "https://nelikvidi.com/sell?sort=-date"
        self.core = 'https://nelikvidi.com'
        self.proxy = False
        self.current_proxy_ip = 0
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
        self.start_page = 1

    def parse(self):
        successful = 0
        while not successful:
            time.sleep(random.randint(1, 3))
            try:
                last_page = self.get_last_page()
                successful = 1
            except Exception as ex:
                print(ex)
                self.change_proxy()
        if self.last_page:
            last_page = int(self.last_page)
        print(f'LAST PAGE {last_page}')
        for i in range(self.start_page, last_page+1):
            print(f'[nelikvidy] page = {i}')
            successful = 0
            while not successful:
                time.sleep(random.randint(1, 3))
                try:
                    soup = self.get_page_soup(self.url+f'&page={i}')
                    result = self.get_offers_from_page(soup)
                    if result:
                        self.send_result(result)
                        successful = 1
                except Exception as ex:
                    print(ex, 111)
                    self.change_proxy()
        change_parser_status('nelikvidy', 'Выкл')
        sys.exit()

    def send_result(self, result):
        for offer in result:
            offer.post(self.db_manager)
        self.db_manager.task_manager()

    def get_offers_from_page(self, soup):
        try:
            offers = soup.find("div", attrs={"class": "items-container"})
            offers = offers.find_all("div", attrs={"class": "table-card img-card catalog-cart"})
            test = offers[1]
        except:
            return False
        answer = []
        for offer in offers:
            link_obj = offer.find("div", attrs={"class": "card-title"}).find("a")
            link = link_obj.attrs['href']
            name = link_obj.attrs['title'].replace('"', '')
            region = offer.find("div", attrs={"class": "card-subtitle"}).find("span")
            date = offer.find("div", attrs={"class": "action-left"}).find_all("span", attrs={"class": "doit"})[1]
            date = date.find("span", attrs={"class": "btn-icon"}).find("small")
            price = offer.find("p", attrs={"class": "formated_price"})
            from_id = link.split('-')[-1].replace('.html', '')
            try:
                a_data = offer.find("div", attrs={"class": "card-side"}).find_all("div")[1].getText()
            except:
                a_data = name
            try:
                company = region.find("a").getText().replace('"', '')
            except:
                company = None

            if date:
                date = self.make_date_good(date.getText())
            else:
                date = None
            if price:
                price = price.getText()
                price = price.split(',')[0]
                price = price.replace(' ', '')
                price = int(price)
            if region:
                region = self.make_region_good(region)
                # region = region.split(' ')[-1][:-1]
            else:
                region = None
            # вычленение "(Имя компании)" из названия заявки
            v = name.split('(')
            v.remove(v[-1])
            e = ''
            i = 1
            for x in v:
                if i == 1:
                    e += x
                else:
                    e += f'({x}'
                i += 1
            name = e

            offer_obj = {"name": name.replace('"', ''), "location": region, "home_name": "nelikvidi",
                                        "offer_start_date": str(date),
                                        "offer_price": price,
                                        "additional_data": a_data.replace('"', ''), "organisation": company, "url": link,
                                        "from_id": from_id
                                        }
            offer = Item(name.replace('"', ''), "nelikvidi", link, region, str(date), None,
                None, None, price, a_data.replace('"', ''), company, from_id,
                None, None)
            answer.append(offer)
        return answer

    def make_region_good(self, region):
        region = region.find("span").getText()
        region = region.split(' ')
        if '\xa0во' in region:
            region.remove('\xa0во')
        if '\xa0в' in region:
            region.remove('\xa0в')

        if region[-1][-1:] == 'и':
            if len(region) == 2:
                region[0] = region[0][:-2]+'ая'
                region[1] = region[1][:-1]+'ь'
            else:
                region[0] = region[0][:-1]+'ь'
        if region[-1][-1:] == 'е':
            if len(region) == 2:
                if region[1] == 'Крае' or region[1] == 'крае':
                    region[1] = region[1][:-1]+'й'
                else:
                    region[1] = region[1][:-1]
                region[0] = region[0][:-2]+'ий'
            else:
                if region[0] == 'Москве' or region[0] == 'Уфе' or region[0] == 'Йошкар-Оле' or region[0] == 'Вологде' or region[0] == 'Калуге':
                    region[0] = region[0][:-1]+'а'
                elif region[0] == 'Симферополе':
                    region[0] = region[0][:-1] + 'ь'
                else:
                    region[0] = region[0][:-1]

        i, good = 1, ''
        for x in region:
            if i == 1:
                good = f'{x}'
            else:
                good = good+f' {x}'
            i += 1
        return good

    def make_date_good(self, date):
        line = date.split(' ')
        try:
            year = int(line[-2].replace(',', ''))
            line.pop(-2)
        except:
            year = datetime.date.today().year

        month = line[-2].replace('.', '').replace(',', '')
        day = line[-3]
        month = self.monthlist[f'{month}']
        date = datetime.date(year, int(month), int(day))
        return date

    def get_last_page(self):
        soup = self.get_page_soup(self.url+'&page=5000')
        last_page = soup.find("ul", attrs={"class": "pagination"}).find("li", attrs={"class": "active"}).getText()
        return int(last_page)

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
                    'User-Agent': UserAgent().chrome}, proxies=self.proxy, timeout=5).content.decode("utf8")
            except:
                print('[nelikvidy] get_page_soup: не получилось сделать запрос с прокси. спим, меняем прокси и снова..')
                return False
        else:
            response = requests.get(url, headers={
                'User-Agent': UserAgent().chrome}).content.decode("utf8")
        soup = BeautifulSoup(response, 'html.parser')
        # print(response)
        return soup


if __name__ == '__main__':
    parser = ParserNelikvidy(False, False)
    parser.parse()
