import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from connector import change_parser_status
from ENGINE import Parser
import time
import random
import datetime
from mixins import proxy_data, get_proxy


class RoseltorgParser(Parser):
    def __init__(self, end):
        super().__init__()
        self.url = "https://www.roseltorg.ru"
        self.sale_url = self.url+"/search/sale?status%5B%5D=0&category%5B%5D=273&category%5B%5D=274&category%5B%5D=275&category%5B%5D=276&category%5B%5D=277&category%5B%5D=278&category%5B%5D=279&category%5B%5D=280&category%5B%5D=281&category%5B%5D=282&category%5B%5D=283&category%5B%5D=284&category%5B%5D=285&category%5B%5D=286&category%5B%5D=287&category%5B%5D=288&category%5B%5D=289&category%5B%5D=290&category%5B%5D=291&category%5B%5D=292&category%5B%5D=293&category%5B%5D=294&category%5B%5D=295&category%5B%5D=296&category%5B%5D=297&category%5B%5D=298&category%5B%5D=299&category%5B%5D=300&category%5B%5D=301&category%5B%5D=302&category%5B%5D=303&category%5B%5D=304&category%5B%5D=305&category%5B%5D=306&category%5B%5D=307&category%5B%5D=308&category%5B%5D=309&category%5B%5D=310&category%5B%5D=311&category%5B%5D=312&category%5B%5D=313&category%5B%5D=314&category%5B%5D=315&category%5B%5D=316&category%5B%5D=317&category%5B%5D=318&category%5B%5D=319&category%5B%5D=320&category%5B%5D=321&category%5B%5D=322&category%5B%5D=323&category%5B%5D=324&category%5B%5D=325&category%5B%5D=326&category%5B%5D=327&category%5B%5D=329&category%5B%5D=330&currency=all&page={}&from={}"
        self.proxy_mode = False
        self.start_page = 1
        self.last_page = end

    def parse(self):
        successful = 0
        while not successful:
            time.sleep(random.randint(1, 4))
            try:
                last_page = self.get_last_page()
                successful = 1
            except Exception as ex:
                print(ex)
                self.change_proxy()
        if self.last_page:
            last_page = int(self.last_page)
        for i in range(self.start_page, last_page + 1):
            print(i)
            time.sleep(10)
            successful = 0
            while not successful:
                time.sleep(random.randint(1, 15))
                try:
                    self.soup = self.get_page_soup(self.sale_url.format(i, i * 10))
                    result = self.get_offers_from_page(self.soup)
                    if result:
                        self.send_result(result)
                        successful = 1
                    else:
                        self.change_proxy()
                except Exception as ex:
                    print(ex)
                    self.change_proxy()
        change_parser_status('roseltorg', 'Выкл')

    def send_result(self, data):
        for offer in data:
            z = requests.post("https://synrate.ru/api/offers/create",
                              json=offer)
            today = datetime.datetime.today().strftime('%d-%m %H:%M')
            try:
                print(f'[roseltorg] {z.json()}\n{offer}')
                # with open('/var/www/synrate_dir/roseltorg.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z.json()}\n{offer}')
                #     f.close()
            except:
                print(f'[roseltorg] {z}\n{offer}')
                # with open('/var/www/synrate_dir/roseltorg.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z}\n{offer}')
                #     f.close()

    def get_offers_from_page(self, soup):
        try:
            offers = self.soup.find_all("div", {"class": "search-results__item"})
            test = offers[0]
        except Exception as ex:
            print(ex)
            return False
        answer = []
        for offer in offers:
            link_obj = offer.find("div", attrs={"class": "search-results__subject"}).find("a", attrs={"class": "search-results__link"})
            link = self.url+link_obj.attrs['href']
            name = link_obj.getText()
            company = offer.find("div", attrs={"class": "search-results__customer"}).find("p")
            price = offer.find("div", attrs={"class": "search-results__sum"})
            region = offer.find("div", attrs={"class": "search-results__region"})
            end_date = offer.find("time", attrs={"class": "search-results__time"})

            if region:
                region = region.find("p").getText()
                region = self.make_region_good(region)
            else:
                region = None
            if price:
                price = price.find("p").getText()
                price = self.make_price_good(price)
            else:
                price = None
            if end_date:
                end_date = end_date.getText()
                end_date = self.make_date_good(end_date)
            else:
                end_date = None
            if company:
                company = company.getText().replace('"', '')
            else:
                company = None

            offer_obj = {"name": name, "location": region, "home_name": "roseltorg",
             "offer_type": "Продажа",# "offer_start_date": str(publish_date),
             "offer_end_date": end_date,
             "owner": "недоступно", "ownercontact": "временно недоступно",
             "offer_price": price,
             # "subcategory": "Не определена",
             # "category": "Не определена",
             "additional_data": name, "organisation": company,
             "url": link
             }
            answer.append(offer_obj)

        return answer

    def make_price_good(self, price):
        price = price.split(',')[0].replace(' ', '')
        return int(price)

    def make_date_good(self, date):
        by_points = date.split('.')
        day, month = by_points[0], by_points[1]
        year = by_points[2].split(" ")[0]
        date = f'{year}-{month}-{day}'
        return date

    def make_region_good(self, region):
        region = region.split('.')[1].replace(' ', '')
        return region

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
                    'User-Agent': UserAgent().chrome}, proxies=proxy, timeout=5)#.content.decode("utf8")
                response.encoding = 'utf-8'
                response = response.content
            except Exception as ex:
                print('get_page_soup: не получилось сделать запрос с прокси. спим, меняем прокси и снова..',
                      f'\n{url}\n\n{ex}')
                time.sleep(2)
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
                print(f'[roseltorg] new proxy_mode {self.proxy_mode}')
                time.sleep(random.randint(1, 4))
                return True
            except:
                pass
        self.proxy_mode = 1
        # if self.proxy_mode > 1:
        #     time.sleep(300)
        print(f'[roseltorg] new proxy_mode {self.proxy_mode}')
        time.sleep(random.randint(1, 4))
        return False

    # сайт не показывает последнюю страницу, но мы можем перейти на нее используя баг
    # сайт перекинет на ласт страницу, если укажем page больше чем их на самом деле и from=10
    # уберете фром и скажет, что стр. 500 нет. надо с from
    def get_last_page(self):
        soup = self.get_page_soup(self.sale_url.format(500, 10))
        last_page = soup.find("a", attrs={"class": "pagination__link pagination__link--active"}).getText()
        last_page = last_page.split(' ')[-1]
        return int(last_page)


if __name__ == '__main__':
    parser = RoseltorgParser()
    parser.parse()
