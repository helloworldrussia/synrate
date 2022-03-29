import random
import time

import undetected_chromedriver as uc
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from selenium import webdriver
from lxml import html
from urllib3 import Retry

from ENGINE import Parser
import requests
from bs4 import BeautifulSoup
import datetime

from mixins import get_proxy

headers = {
    "content-type": "text/plain",
    "content-lenght": "2144",
    "accept-language": "ru,en;q=0.9",
    'User-Agent': UserAgent().opera
}


class ParserTektorg(Parser):
    def __init__(self):
        super(ParserTektorg, self).__init__()
        self.list_url = "https://www.tektorg.ru/sale/procedures?lang=ru&q="
        self.item_urls = []
        self.proxy_mode = 1

    def parse(self):
        last_page = self.get_last_page()
        for i in range(1, 30):

            urls = (self.soup.find_all("a", attrs={"class": "section-procurement__item-title"}))
            for url in urls:
                self.item_urls.append(url["href"])
        for url in self.item_urls:
            if url.find("vitrina") != -1:
                self.item_urls.remove(url)
        for url in self.item_urls:
            name = None
            item_url = "https://www.tektorg.ru" + url
            region = None
            fin_date = None
            org_name = None
            org_phone = None
            org_owner = None
            start_date = None
            # self.response = requests.get("https://www.tektorg.ru"+url, headers={'User-Agent': UserAgent().chrome}).text


            # self.soup = BeautifulSoup(content,#self.response,
            #                           'html.parser')
            try:
                name = self.soup.find("span", attrs={"class": "procedure__item-name"}).getText()
            except AttributeError:
                name = None
            tables = self.soup.find_all("table", attrs={"class": "procedure__item-table"})
            for table in tables:
                table_rows = table.find_all("tr")
                for row in table_rows:
                    try:
                        z = row.find_all("td")[0]
                    except IndexError:
                        continue
                    if row.find_all("td")[0].getText() == "Регион поставки:":
                        try:
                            region = row.find_all("td")[1].getText()
                        except (IndexError, AttributeError):
                            region = None
                    if row.find_all("td")[0].getText().strip() == "Дата публикации процедуры:":
                        try:
                            start_date = row.find_all("td")[1].getText().split(" ")[0].replace(u".", "-")
                            print(row.find_all("td")[1].getText().split(" ")[0])
                        except (IndexError, AttributeError):
                            start_date = None
                    if row.find_all("td")[0].getText().strip() == "Дата окончания приема заявок:":
                        try:
                            fin_date = row.find_all("td")[1].getText().split(" ")[0].replace(u".", "-")
                        except (IndexError, AttributeError):
                            fin_date = ""
                    if row.find_all("td")[0].getText().strip() == "Наименование организатора:":
                        try:
                            org_name = row.find_all("td")[1].getText().strip()
                        except (IndexError, AttributeError):
                            org_name = ""
                    if row.find_all("td")[0].getText().strip() == "Контактный телефон:":
                        try:
                            org_phone = row.find_all("td")[1].getText().strip()
                        except (IndexError, AttributeError):
                            org_phone = None
                    if row.find_all("td")[0].getText().strip() == "ФИО контактного лица:":
                        try:
                            org_owner = row.find_all("td")[1].getText().strip()
                        except (IndexError, AttributeError):
                            org_owner = ""


            try:
                start_date = start_date.split("-")[2] + "-" + start_date.split("-")[1] + "-" + start_date.split("-")[0]
            except AttributeError:
                start_date = None
            try:
                fin_date = fin_date.split("-")[2] + "-" + fin_date.split("-")[1] + "-" + fin_date.split("-")[0]
            except AttributeError:
                fin_date = datetime.date.today() + datetime.timedelta(days=3)
            if org_owner is None:
                org_owner = ""
            if name is None:
                continue
            print(start_date, fin_date)
            J = {"name": name.replace('"', ''), "location": "РФ", "home_name": "tektorg",
                                    "offer_type": "Продажа",
                                    #"offer_start_date": str(start_date),
                                    #"offer_end_date": str(fin_date),
                                    "owner": org_owner.replace('"', ''), "ownercontact": org_phone, "offer_price": 0,
                                    "additional_data": "не указано", "organisation": org_name.replace('"', ''),
                                    "url": item_url
                                    #"category": "Не определена", "subcategory": "не определена"
                      }

            if start_date is not None:
                J["offer_start_date"] = str(start_date)
            if fin_date is not None:
                J["offer_end_date"] = str(fin_date)

            z = requests.post("https://synrate.ru/api/offers/create",
                              json=J)

            # TESTING -------------
            print(f'TECH: {z.json()}  {J}')
            time.sleep(random.randint(1, 5) / 10)
            # ---------------------

    def get_last_page(self):
        soup = self.get_page_soup(self.list_url+'&page=1', self.proxy_mode)
        last_page = soup.find("ul", attrs={"class": "pagination"}).find_all("li")[-2].find("a").getText()
        print(last_page)

    def get_page_soup(self, url, proxy):
        if proxy:
            proxy = get_proxy(proxy)
            # proxy_status = check_proxy(proxy)
            try:
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                response = session.get(url, headers=headers, proxies=proxy, timeout=5).content.decode("utf8")
                soup = BeautifulSoup(response, 'html.parser')
            except:
                print('get_page_soup: не получилось сделать запрос с прокси. спим, меняем прокси и снова..')
                return False
        else:
            response = requests.get(url, headers=headers).content.decode("utf8")
            soup = BeautifulSoup(response, 'html.parser')
        print(response)
        return soup


if __name__ == '__main__':
    z = ParserTektorg()
    z.parse()
