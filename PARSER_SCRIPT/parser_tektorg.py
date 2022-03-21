import random
import time

import undetected_chromedriver as uc
from fake_useragent import UserAgent
from selenium import webdriver
from lxml import html
#from webdriver_manager.firefox import GeckoDriverManager

from ENGINE import Parser
import requests
from bs4 import BeautifulSoup
import datetime


class ParserTektorg(Parser):
    def __init__(self):
        super(ParserTektorg, self).__init__()
        self.list_url = "https://www.tektorg.ru/procedures?lang=ru&q=&page={}"
        self.item_urls = []

    def parse(self):
#        opts = undetected_chromedriver.ChromeOptions()
#        opts.headless = True
        # driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=opts)
        # core = GeckoDriverManager().install()
        options = webdriver.ChromeOptions()
        options.headless=True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        driver = uc.Chrome(options=options)
        frills(driver)
        for i in range(1, 3):
            # ---------
            print(f'new itarion {i}/30')
            driver.get(self.list_url.format(i))
            try:
                content = driver.page_source
            except:
                print('Some problems... TECHTORG')
                continue
            tree = html.fromstring(content)
            # ---------
            # self.response = requests.get(f"{self.list_url.format(i)}&", headers={'User-Agent': UserAgent().chrome}, verify=False).content.decode("utf8") #"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"}).text
            self.soup = BeautifulSoup(content, 'html.parser')#self.response, 'html.parser')
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
            driver.get(f'https://www.tektorg.ru{url}')
            content = driver.page_source
            self.soup = BeautifulSoup(content,#self.response,
                                      'html.parser')
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
                        except (IndexError, AttributeError):
                            start_date = None
                    if row.find_all("td")[0].getText().strip() == "Дата окончания приема заявок:":
                        try:
                            fin_date = row.find_all("td")[1].getText().split(" ")[0].replace(u".", "-")
                        except (IndexError, AttributeError):
                            fin_date = None
                    if row.find_all("td")[0].getText().strip() == "Наименование организатора:":
                        try:
                            org_name = row.find_all("td")[1].getText().strip()
                        except (IndexError, AttributeError):
                            org_name = None
                    if row.find_all("td")[0].getText().strip() == "Контактный телефон:":
                        try:
                            org_phone = row.find_all("td")[1].getText().strip()
                        except (IndexError, AttributeError):
                            org_phone = None
                    if row.find_all("td")[0].getText().strip() == "ФИО контактного лица:":
                        try:
                            org_owner = row.find_all("td")[1].getText().strip()
                        except (IndexError, AttributeError):
                            org_owner = None


            try:
                start_date = start_date.split("-")[2] + "-" + start_date.split("-")[1] + "-" + start_date.split("-")[0]
            except AttributeError:
                start_date = None
            try:
                fin_date = fin_date.split("-")[2] + "-" + fin_date.split("-")[1] + "-" + fin_date.split("-")[0]
            except AttributeError:
                fin_date = datetime.date.today() + datetime.timedelta(days=3)

            z = requests.post("https://synrate.ru/api/offers/create",
                              json={"name": name.replace('"', ''), "location": "РФ", "home_name": "tektorg",
                                    "offer_type": "Продажа", "offer_start_date": str(start_date),
                                    "offer_end_date": str(fin_date),
                                    "owner": org_owner.replace('"', ''), "ownercontact": org_phone, "offer_price": 0,
                                    "additional_data": "не указано", "organisation": org_name.replace('"', ''), "url": item_url,
                                    "category": "Не определена", "subcategory": "не определена"})

            # TESTING -------------
            J = {"name": name.replace('"', ''), "location": "РФ", "home_name": "tektorg",
                                    "offer_type": "Продажа", "offer_start_date": str(start_date),
                                    "offer_end_date": str(fin_date),
                                    "owner": org_owner.replace('"', ''), "ownercontact": org_phone, "offer_price": 0,
                                    "additional_data": "не указано", "organisation": org_name.replace('"', ''), "url": item_url,
                                    "category": "Не определена", "subcategory": "не определена"}
            print(f'TECH: {z.json()}  {J}')
            time.sleep(random.randint(1, 5) / 10)
            # ---------------------


def frills(driver):
    print('Frilling u know')
    driver.get('https://yandex.ru/images/')
    time.sleep(random.randint(1, 4))
    driver.get('https://yandex.ru')
    time.sleep(random.randint(1, 4))
    driver.get('https://yandex.ru/search/?lr=50&text=погода+в+москве')
    print('Ok.. thats all.')


if __name__ == '__main__':
    z = ParserTektorg()
    z.parse()
