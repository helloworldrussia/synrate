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
import sys


class ParserEtpActiv(Parser):

    def __init__(self, verify, end):
        super.__init__
        self.verify = verify
        self.url = "https://etp-aktiv.ru/catalog/"
        self.procedure_id = None
        self.response_item = None
        self.core = 'https://etp-aktiv.ru'
        self.core_www = 'https://www.etp-aktiv.ru'
        self.proxy = False
        self.current_proxy_ip = 0
        self.last_page = end

    def parse(self):
        last_page = self.get_last_page()
        if self.last_page:
            last_page = int(self.last_page)
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
                print(f'etp-activ: Обрабатываем страницу - {page_url}\nproxy_mode: {self.current_proxy_ip}')
            # time.sleep(random.randint(1, 3))
        change_parser_status('etp_aktiv', 'Выкл')
        sys.exit()

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
                'User-Agent': UserAgent().chrome},
                                    verify=self.verify).content.decode("utf8")
        soup = BeautifulSoup(response, 'html.parser')
        # print(response)
        return soup

    def get_last_page(self):
        successful = 0
        while not successful:
            try:
                soup = self.get_page_soup(self.url)
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
        self.proxy, self.current_proxy_ip = get_proxy(self.current_proxy_ip)
        time.sleep(30)

    def get_page_offers(self, url):

        soup = self.get_page_soup(url)
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
            from_id = link.split('/')[-2]

            offer_obj = {"name": name,
                 "home_name": "etp-activ",
                 #"offer_start_date": start_date, "offer_end_date": end_date,
                 "additional_data": text,# "organisation": company,
                 "url": link, "from_id": from_id}
            if region is not None:
                offer_obj['location'] = region.getText().replace('\n', '').replace(' ', '')
            else:
                region = None

            detail = self.get_detail_info(link)
            for key, value in detail.items():
                offer_obj[f'{key}'] = value
            answer.append(offer_obj)
        return answer

    def get_detail_info(self, url):
        company, region, category = None, None, None
        soup = self.get_page_soup(url)
        p = soup.find("div", attrs={"class": "detail-product__content"}).find_all("p")
        name = soup.find("h1", attrs={"class": "detail-product__title"}).getText()
        params = soup.find("div", attrs={"class": "detail-product__header-content-info"}).find_all("dl")
        try:
            price = soup.find("div", attrs={"class": "detail-product__header-buy-price-value"}).getText()
            price = price.replace(' ', '').replace('\n', '')
        except:
            price = None
        for param in params:
            title = param.find("dt").getText()
            if title == "Продавец":
                company = param.find("dd").getText().replace('"', '')
            if title == "Регион":
                region = param.find("dd").getText()
            if title == "Категория":
                category = param.find("dd").getText().replace('"', '')

        a_data = ''
        for x in p:
            a_data = a_data+x.getText().replace('"', '')
        answer = {
            # "home": url,
            "name": name, "price": price, "owner": company,
            "location": region, "additional_data": a_data, "short_cat": category
        }

        # print('ANSWER:', answer)
        return answer

    def post_result(self, data):
        for offer in data:
            z = requests.post("https://synrate.ru/api/offers/create",
                              json=offer)
            today = datetime.today().strftime('%d-%m %H:%M')
            try:
                print(f'[etp_aktiv] {z.json()}\n{offer}')
                # with open('/var/www/synrate_dir/b2b-center.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z.json()}\n{offer}')
                #     f.close()
            except:
                print(f'[etp_aktiv] {z}\n{offer}')
                # with open('/var/www/synrate_dir/b2b-center.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z}\n{offer}')
                #     f.close()
            try:
                id = z.json()['unique_error'][0]
                z = requests.put(f"https://synrate.ru/api/offer/update/{id}/",
                                 json=offer)
            except:
                pass
            try:
                print(f'[etp_aktiv] {z.json()}\n{offer}')
                # with open('/var/www/synrate_dir/b2b-center.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z.json()}\n{offer}')
                #     f.close()
            except:
                print(f'[etp_aktiv] {z}\n{offer}')
                # with open('/var/www/synrate_dir/b2b-center.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z}\n{offer}')
                #     f.close()


if __name__ == '__main__':
    Parser = ParserEtpActiv(True, False)
    Parser.parse()
