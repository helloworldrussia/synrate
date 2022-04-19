import random
import sys
import time
from datetime import datetime
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter, Retry
from connector import change_parser_status, Item
from ENGINE import Parser
import requests
from bs4 import BeautifulSoup
from mixins import get_proxy


class ParserCenter(Parser):

    def __init__(self, verify, end):
        super.__init__
        self.url = "https://www.b2b-center.ru/market/?searching=1&company_type=2&price_currency=0&date=1&trade=sell&lot_type=0"
        self.procedure_id = None
        self.response_item = None
        self.core = 'https://b2b-center.ru'
        self.core_www = 'https://www.b2b-center.ru'
        self.verify = verify
        # значение либо int (соотвествующее желаемому прокси из mixins.proxy_data), либо False - прокси не используем
        self.proxy = False
        self.last_page = end
        self.current_proxy_ip = 0

    def parse(self):
        # делаем запрос, получаем суп и отдаем функции, получающей номер последней страницы
        last_page = self.get_last_page()
        print(last_page)
        if self.last_page:
            last_page = int(self.last_page)
        # time.sleep(random.randint(1, 3))
        i = 1
        # for page in range(1, 2):
        for page in range(1, int(last_page)+1):
            time.sleep(random.randint(5, 10))
            page_url = self.url + f'&page={page}&from={10 * int(page)}'
            # проходим страницу пока не получим результат.
            # если результат Flase - нас задетектили, повторяем.
            # get_offers_from_page сама сменит/включит прокси и вернет False, если поймет, что анти-парсер нас засек
            successful = 0
            while not successful:
                time.sleep(random.randint(1, 7))
                print('Обработка:', page_url)
                soup = self.get_page_soup(page_url)
                result = self.get_offers_from_page(soup)
                if result:
                    successful = 1
                print(f'\nproxy_mode: {self.current_proxy_ip}')
                # time.sleep(random.randint(1, 5))
            # счетчик успешно пройденных страниц
            if i == 20:
                # print('Большая пауза. Диапазон 300-600 секунд.')
                # time.sleep(random.randint(300, 600))
                i = 0
            i += 1
            self.post_result(result)
        change_parser_status('b2b_center', 'Выкл')
        sys.exit()

    def get_offers_from_page(self, soup):
        # проверяем поймал ли нас анти-парсер сайта.
        try:
            main = soup.find("div", attrs={"id": "page"}).find("main").find("section").find_all("div", attrs={"class": "inner"})
        except:
            print(self.current_proxy_ip)
            print(self.change_proxy())
            print(self.current_proxy_ip)
            return False
        i = 1
        for x in main:
            if i == 3:
                main = x
            i += 1
        main = main.table.tbody.find_all("tr")
        offers = main
        answer = []
        for offer in offers:
            dates = offer.find_all("td", attrs={"class": "nowrap"})
            link_obj = offer.find("td").find("a")
            from_id = link_obj.getText()
            name = offer.find("div", attrs={"class": "search-results-title-desc"}).getText().replace('"', '')
            company = offer.find_all("a", attrs={"class": "visited"})[1].getText().replace('"', '')

            start_date, end_date = self.get_dates(dates)
            link = link_obj.attrs['href']
            link = self.core_www+link.replace(self.core, '').replace(self.core_www, '')
            text = name
            from_id = from_id.split('№')[1].split(" ")[1]
            if name is None or name == '':
                continue
            offer_obj = {"name": name,
                         "home_name": "b2b-center",
                         "offer_start_date": start_date, "offer_end_date": end_date,
                         "additional_data": text, "organisation": company,
                         "url": link, "from_id": from_id
                         }
            offer = Item(name, "b2b-center", link, None, start_date, end_date,
                None, None, None, text, company, from_id, None, None)
            answer.append(offer)
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
        if self.current_proxy_ip:
            # proxy_status = check_proxy(proxy)
            try:
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                response = session.get(url, headers={
                    'User-Agent': UserAgent().chrome}, proxies=self.proxy, timeout=5).content.decode("utf8")
                soup = BeautifulSoup(response, 'html.parser')
            except:
                print('get_page_soup: не получилось сделать запрос с прокси. спим, меняем прокси и снова..')
                return False
        else:
            response = requests.get(url, headers={
                'User-Agent': UserAgent().chrome}).content.decode("utf8")
            soup = BeautifulSoup(response, 'html.parser')
        return soup

    def change_proxy(self):
        print('change_proxy: start')
        self.proxy, self.current_proxy_ip = get_proxy(self.current_proxy_ip)
        time.sleep(30)

    def get_last_page(self):
        successful = 0
        while not successful:
            try:
                if self.current_proxy_ip:
                    soup = self.get_page_soup(self.url + '&page=1&from=10#search-result')
                else:
                    soup = self.get_page_soup(self.url + '&page=1&from=10#search-result')
                pagination = soup.find("div", attrs={"class": "pagi"}).find("ul", attrs={"class": "pagi-list"}).find_all("li", attrs={"class": "pagi-item"})
                last_page = pagination[-1].find("a").getText()
                successful = 1
                time.sleep(random.randint(1, 5))
            except Exception as ex:
                print(ex)
                print('get_last_page: Не смогли определить last_page')
                print('proxy_mode: ', self.current_proxy_ip)
                print(self.change_proxy())
                print('proxy_mode: ', self.current_proxy_ip)
                time.sleep(random.randint(1, 5))
        return last_page

    def post_result(self, data):
        for offer in data:
            offer.post()
            # z = requests.post("https://synrate.ru/api/offers/create",
            #                   json=offer)
            # today = datetime.today().strftime('%d-%m %H:%M')
            # try:
            #     print(f'[b2b-center] {z.json()}\n{offer}')
            #     # with open('/var/www/synrate_dir/b2b-center.txt', 'r+') as f:
            #     #     # ...
            #     #     f.seek(0, 2)
            #     #     f.write(f'[{today}] {z.json()}\n{offer}')
            #     #     f.close()
            # except:
            #     print(f'[b2b-center] {z}\n{offer}')
            #     # with open('/var/www/synrate_dir/b2b-center.txt', 'r+') as f:
            #     #     # ...
            #     #     f.seek(0, 2)
            #     #     f.write(f'[{today}] {z}\n{offer}')
            #     #     f.close()
            # try:
            #     id = z.json()['unique_error'][0]
            #     z = requests.put(f"https://synrate.ru/api/offer/update/{id}/",
            #                       json=offer)
            # except:
            #     pass
            # try:
            #     print(f'[b2b-center] {z.json()}\n{offer}')
            #     # with open('/var/www/synrate_dir/b2b-center.txt', 'r+') as f:
            #     #     # ...
            #     #     f.seek(0, 2)
            #     #     f.write(f'[{today}] {z.json()}\n{offer}')
            #     #     f.close()
            # except:
            #     print(f'[b2b-center] {z}\n{offer}')
            #     # with open('/var/www/synrate_dir/b2b-center.txt', 'r+') as f:
            #     #     # ...
            #     #     f.seek(0, 2)
            #     #     f.write(f'[{today}] {z}\n{offer}')
            #     #     f.close()


if __name__ == '__main__':
    Parser = ParserCenter(False, False)
    Parser.parse()
