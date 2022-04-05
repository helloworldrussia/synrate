import random
import time
from datetime import datetime

from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter, Retry
from connector import change_parser_status
from ENGINE import Parser
import requests
from bs4 import BeautifulSoup
from mixins import get_proxy, proxy_data


class ParserEtpgpb(Parser):
    def __init__(self, end):
        super.__init__
        self.url = "https://etpgpb.ru/procedures/?procedure%5Bcategory%5D=actual&procedure%5Bsection%5D%5B2%5D=nelikvid"
        self.procedure_id = None
        self.response_item = None
        self.core = 'https://etpgpb.ru'
        self.proxy_mode = False
        self.last_page = end

    def parse(self):
        # делаем запрос, получаем суп и отдаем функции, получающей номер последней страницы
        # self.response = requests.get(self.url, headers={
        #     'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36"})
        # self.response.encoding = 'utf-8'
        # self.soup = BeautifulSoup(self.response.content, 'html.parser')
        last_page = self.get_last_page()
        if self.last_page:
            last_page = int(self.last_page)
        # запускаем цикл сбора информации с каждой страницы
        results = 0
        for page in range(1, int(last_page)+1):
            successful = 0
            while not successful:
                time.sleep(random.randint(1, 7))
                print(f'etpgpb: Сканируем стр. {page}\nproxy_mode: {self.proxy_mode}')
                page_soup = self.get_page_soup(self.url+f'&page={page}', self.proxy_mode)
                result = self.get_offers(page_soup, self.core)
                if result:
                    successful = 1
                    self.send_result(result)
        change_parser_status('etpgpb', 'Выкл')
        print(f'Закончили len = {results}')

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
                'User-Agent': UserAgent().chrome}).content.decode("utf8")
        soup = BeautifulSoup(response, 'html.parser')
        # print(response)
        return soup

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

    def get_offers(self, soup, core):
        # вытаскиваем информацию из дивов заявок в словари, те в список и возвращаем
        try:
            offers_list = soup.find_all("div", attrs={"class": "procedure"})
        except:
            self.change_proxy()
            return False
        cleaned_data = []
        end_date = None
        start_date = None
        region = None
        company = None
        text = None
        for offer in offers_list:

            # вытаскиваем нужные данные в переменные
            link = core+offer.find("a", attrs={"class": "procedure__link"}).attrs['href']
            company = offer.find("div", attrs={"class": "procedure__companyName"}).getText()
            name = offer.find("div", attrs={"class": "procedure__infoDescriptionFull"}).getText() # ниже посмотри !!!
            divs = offer.find("div", attrs={"class": "procedure__details"}).find_all("div", attrs={"class": "procedure__detailsUnitValue"}) # пропиши функцию для обработки даты!!!
            text = offer.find("div", attrs={"class": "procedure__infoDescriptionFull"}).getText()
            price = offer.find("div", attrs={"class": "procedure__detailsSum"})
            if price is not None:
                price = price.getText()
            else:
                price = None
            offer_type = offer.find("div", attrs={"class": "procedure__infoAuctionType"}).getText()

            divs_texts = []
            for x in divs:
                divs_texts.append(x.getText())
                # print(x.getText())

            if len(divs_texts) == 3:
                start_date, end_date = self.get_date_from_details(link)
                region = divs_texts[2]
            elif len(divs_texts) == 5 and divs_texts[4] == '':
                start_date = divs_texts[3]
                region = divs_texts[2]
            elif len(divs_texts) == 5:
                end_date = divs_texts[0]
                start_date = divs_texts[3]
                region = divs_texts[2]
                main_day = divs_texts[4] # дата аукциона

            # отправляем значения, которые имеют неверный для нас формат, на реплейсы и сплиты
            price = self.make_price_good(price)
            start_date = self.make_date_good(start_date)
            end_date = self.make_date_good(end_date)

            # формируем словарь из полученных данных и добавляем в список
            data_dict = {"name": name, "location": region, "home_name": "etpgpb",
                                        "offer_type": offer_type, "offer_start_date": start_date, "offer_end_date": end_date,
                                        #"owner": None, "ownercontact": None,
                                        "offer_price": price,
                                        "additional_data": text, "organisation": company, "url": link
                                        #"category": "Не определена", "subcategory": "не определена"
                                        }

            cleaned_data.append(data_dict)
        # передаем список из словарей с информацией о заявках обратно
        return cleaned_data

    def get_date_from_details(self, url):
        response = requests.get(url, headers={
            'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36"})
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        dates_dirty = soup.find("div", attrs={"class": "block__docs_lot_content", "style": "display: block;"})
        dates_dirty = dates_dirty.find_all("p", attrs={"class": "block__docs_container_info"})
        # print(dates_dirty, dates)
        dates = []
        for x in dates_dirty:
            dates.append(x.getText().split(" ")[0])
        end_date = dates[0]

        start_date = soup.find("p", attrs={"class": "block__docs_container_info datePublished"}).getText()
        return start_date.split(' ')[0], end_date

    def make_date_good(self, date):
        try:
            test = int(date.split('.')[0])
            if date.find(':') or date.find('('):
                date = date.split(' ')[0]
            date = date.split('.')
            date = f"{date[2]}-{date[1]}-{date[0]}"
        except:
            date = None
        return date

    def make_price_good(self, price):
        try:
            split_price = price.split(' ')
            price = price.replace(f'{split_price[-1]}', '').replace(' ', '')
        except:
            price = 0
        return price

    def send_result(self, data):
        for offer in data:
            z = requests.post("https://synrate.ru/api/offers/create",
                              json=offer)
            today = datetime.today().strftime('%d-%m %H:%M')
            try:
                print(f'[etpgpb] {z.json()}\n{offer}')
                # with open('/var/www/synrate_dir/etpgpb.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z.json()}\n{offer}')
                #     f.close()
            except:
                print(f'[etpgpb] {z}\n{offer}')
                # with open('/var/www/synrate_dir/etpgpb.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z}\n{offer}')
                #     f.close()

    def get_last_page(self):
        successful = 0
        while not successful:
            soup = self.get_page_soup(self.url, self.proxy_mode)
            try:
                pag_items = soup.find("div", attrs={"class": "pagination"}).find_all("a", attrs={"class": "pagination__item"})
                last_page = pag_items[-1].getText()
                successful = 1
            except:
                self.change_proxy()
        return last_page


if __name__ == '__main__':
    Parser = ParserEtpgpb()
    Parser.parse()
