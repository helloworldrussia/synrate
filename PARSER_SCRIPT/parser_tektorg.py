from fake_useragent import UserAgent

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
        for i in range(1, 30):
            self.response = requests.get(self.list_url.format(i), headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"}).text
            self.soup = BeautifulSoup(self.response, 'html.parser')
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
            self.response = requests.get("https://www.tektorg.ru"+url, headers={'User-Agent': UserAgent().chrome}).text
            self.soup = BeautifulSoup(self.response, 'html.parser')
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
                              json={"name": name, "location": "РФ", "home_name": "tektorg",
                                    "offer_type": "Продажа", "offer_start_date": str(start_date),
                                    "offer_end_date": str(fin_date),
                                    "owner": org_owner, "ownercontact": org_phone, "offer_price": 0,
                                    "additional_data": "не указано", "organisation": org_name, "url": item_url,
                                    "category": "Не определена", "subcategory": "не определена"})

            # TESTING -------------
            J = {"name": name, "location": "РФ", "home_name": "tektorg",
                                    "offer_type": "Продажа", "offer_start_date": str(start_date),
                                    "offer_end_date": str(fin_date),
                                    "owner": org_owner, "ownercontact": org_phone, "offer_price": 0,
                                    "additional_data": "не указано", "organisation": org_name, "url": item_url,
                                    "category": "Не определена", "subcategory": "не определена"}
            print(z, J)
            # ---------------------


if __name__ == '__main__':
    z = ParserTektorg()
    z.parse()
