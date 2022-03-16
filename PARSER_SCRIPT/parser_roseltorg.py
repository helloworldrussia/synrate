import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from ENGINE import Parser
import time
import random
import datetime


class RoseltorgParser(Parser):
    def __init__(self):
        super().__init__()
        self.url = "https://www.roseltorg.ru"

    def parse(self):
        for i in range(1, 50):
            page_url = self.url+"/procedures/search?sale=0&status%5B%5D=0&currency=all&page={}&from={}".format(i, i*10)
            self.response = requests.get(page_url, headers={'User-Agent': UserAgent().chrome}).content.decode("utf8")
            self.soup = BeautifulSoup(self.response, "html.parser")
            for link in self.soup.find_all("a", {"class": "search-results__link"}):
                self.post_links.append(link.attrs['href'])

        # Удаление дубликатов списка.
        self.post_links = list(set(self.post_links))

        for link in self.post_links:
            lot_name = None
            lot_price = None
            publish_date = None
            finish_date = None
            organisation = None
            self.response = requests.get(self.url+link,
                                         headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36"}).content.decode("utf8")
            self.soup = BeautifulSoup(self.response, "html.parser")
            lots = self.soup.find_all("div", {"class": "lot-item"})
            for lot in lots:
                lot_name = lot.find("div", {"class": "lot-item__subject"}).find("p").getText()

                lot_price = lot.find("div", {"class": "lot-item__sum"}).find("p").getText().split(",")[0].strip()\
                    .replace(" ", "")

                details = lot.find("div", {"class": "hidden-content"})
                date_table = details.find_all("tbody")[0]
                for row in date_table.find_all("tr", {"class": "data-table__item"}):
                    if row.find("span").getText() == "Дата публикации":
                        publish_date = row.find("p").getText().split(" ")[0]
                        z = publish_date.split(".")

                        publish_date = datetime.date(int("20"+z[2]), int(z[1]), int(z[0]))

                    if row.find("span").getText() == "Дата и время окончания подачи заявок":
                        finish_date = row.find("p").getText().split(" ")[1]
                        z = finish_date.split(".")

                        finish_date = datetime.date(int("20"+z[2]), int(z[1]), int(z[0]))
                another_table = details.find_all("tbody")[1]
                for row in another_table.find_all("tr", {"class": "data-table__item"}):
                    if row.find("span"):
                        if row.find("span").getText() == "Название организации (ИНН)":
                            organisation = row.find("p").getText()

                        if row.find("span").getText() == "Почтовый адрес":
                            post_adress = row.find("p").getText()

                        if row.find("span").getText() == "Телефон":
                            phone = row.find("p").getText()

                        if row.find("span").getText() == "E-mail":
                            email = row.find("p").getText()

                        if row.find("span").getText() == "Место поставки":
                            place = row.find("p").getText()
                print("roseltorg created")
                z = requests.post("https://synrate.ru/api/offers/create",
                                  json={"name": lot_name, "location": "РФ", "home_name": "roseltorg",
                                        "offer_type": "Продажа", "offer_start_date": str(publish_date),
                                        "offer_end_date": str(finish_date),
                                        "owner": "недоступно", "ownercontact": "временно недоступно",
                                        "offer_price": lot_price,
                                        "subcategory": "Не определена",
                                        "category": "Не определена",
                                        "additional_data": "не указано", "organisation": organisation,
                                        "url": self.url+link})

                print(f'{z}')
                time.sleep(random.randint(1, 5)/10)


if __name__ == '__main__':
    parser = RoseltorgParser()
    parser.parse()
