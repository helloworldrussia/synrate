import random
import sys
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import datetime
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from connector import change_parser_status
from ENGINE import Parser
from mixins import get_proxy, proxy_data


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
        self.verify = verify
        self.last_page = end
        self.url = "https://nelikvidi.com/sell?sort=-date"
        self.core = 'https://nelikvidi.com'
        self.proxy_mode = False
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

    # def get_start_page(self):
    #     nelikvidy = Info.objects.get(name='nelikvidy')
    #     self.start_page = nelikvidy.start_page

    def parse(self):
        # self.get_start_page() # чтобы начать с места, где остановились
        successful = 0
        while not successful:
            time.sleep(random.randint(1, 15))
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
                time.sleep(random.randint(1, 15))
                try:
                    soup = self.get_page_soup(self.url+f'&page={i}')
                    result = self.get_offers_from_page(soup)
                    if result:
                        self.send_result(result)
                        successful = 1
                except Exception as ex:
                    print(ex)
                    self.change_proxy()
        change_parser_status('nelikvidy', 'Выкл')
        sys.exit()

    def send_result(self, result):
        for offer in result:
            z = requests.post("https://synrate.ru/api/offers/create",
                              json=offer)
            today = datetime.datetime.today().strftime('%d-%m %H:%M')
            try:
                print(f'[nelikvid] {z.json()}\n{offer}')
                # with open('/var/www/synrate_dir/nelikvid.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z.json()}\n{offer}')
                #     f.close()
            except:
                print(f'[nelikvid] {z}\n{offer}')
                # with open('/var/www/synrate_dir/nelikvid.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z}\n{offer}')
                #     f.close()

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
                region = region.find("span").getText()
                region = region.split(' ')[-1][:-1]
            else:
                region = None
            offer_obj = {"name": name.replace('"', ''), "location": region, "home_name": "nelikvidi",
                                        "offer_start_date": str(date),
                                        "offer_price": price,
                                        "additional_data": name.replace('"', ''), "organisation": company, "url": link,
                                        "from_id": from_id
                                        }
            answer.append(offer_obj)

        return answer

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
        print('[nelikvidy] change_proxy: start')
        if self.proxy_mode:
            try:
                a = proxy_data[self.proxy_mode+1]
                self.proxy_mode += 1
                return True
            except:
                pass
        print(f'\n[nelikvidy] proxy_mode: {self.proxy_mode}')
        self.proxy_mode = 1
        if self.proxy_mode > 1:
            time.sleep(300)
        return False

    def get_page_soup(self, url):
        proxy_mode = self.proxy_mode
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
