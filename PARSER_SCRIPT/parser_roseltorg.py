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
            page_url = self.url+"/search/sale?status%5B%5D=0&category%5B%5D=273&category%5B%5D=274&category%5B%5D=275&category%5B%5D=276&category%5B%5D=277&category%5B%5D=278&category%5B%5D=279&category%5B%5D=280&category%5B%5D=281&category%5B%5D=282&category%5B%5D=283&category%5B%5D=284&category%5B%5D=285&category%5B%5D=286&category%5B%5D=287&category%5B%5D=288&category%5B%5D=289&category%5B%5D=290&category%5B%5D=291&category%5B%5D=292&category%5B%5D=293&category%5B%5D=294&category%5B%5D=295&category%5B%5D=296&category%5B%5D=297&category%5B%5D=298&category%5B%5D=299&category%5B%5D=300&category%5B%5D=301&category%5B%5D=302&category%5B%5D=303&category%5B%5D=304&category%5B%5D=305&category%5B%5D=306&category%5B%5D=307&category%5B%5D=308&category%5B%5D=309&category%5B%5D=310&category%5B%5D=311&category%5B%5D=312&category%5B%5D=313&category%5B%5D=314&category%5B%5D=315&category%5B%5D=316&category%5B%5D=317&category%5B%5D=318&category%5B%5D=319&category%5B%5D=320&category%5B%5D=321&category%5B%5D=322&category%5B%5D=323&category%5B%5D=324&category%5B%5D=325&category%5B%5D=326&category%5B%5D=327&category%5B%5D=329&category%5B%5D=330&currency=all&page={}&from={}".format(i, i*10)
            print(page_url)
            self.response = requests.get(page_url, headers={'User-Agent': UserAgent().chrome}).content.decode("utf8")
            self.soup = BeautifulSoup(self.response, "html.parser")
            for link in self.soup.find_all("a", {"class": "search-results__link"}):
                self.post_links.append(link.attrs['href'])
            time.sleep(random.randint(1, 7))
        # Удаление дубликатов списка.
        self.post_links = list(set(self.post_links))

        for link in self.post_links:
            print(link)
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
                # print(lot_name)

                lot_price = lot.find("div", {"class": "lot-item__sum"}).find("p").getText().split(",")[0].strip()\
                    .replace(" ", "")
                # print(lot_price)
                details = lot.find("div", {"class": "hidden-content"})
                date_table = details.find_all("tbody")[0]
                for row in date_table.find_all("tr", {"class": "data-table__item"}):
                    # print(row.find("span").getText(), row.find("p").getText())
                    if row.find("span").getText() == "Дата публикации" or row.find("span").getText() == "Публикация извещения":
                        publish_date = row.find("p").getText().split(" ")[0]
                        z = publish_date.split(".")

                        publish_date = datetime.date(int("20"+z[2]), int(z[1]), int(z[0]))

                    if row.find("span").getText() == "Дата и время окончания подачи заявок":
                        finish_date = row.find("p").getText().split(" ")[1]
                        z = finish_date.split(".")

                        finish_date = datetime.date(int("20"+z[2]), int(z[1]), int(z[0]))
                    if row.find("span").getText() == "Рассмотрение заявок":
                        finish_date = row.find("p").getText().split(" ")[1].split(".")
                        finish_date = datetime.date(int("20"+finish_date[2]), int(finish_date[1]), int(finish_date[0]))

                    if row.find("span").getText() == "Приём заявок":
                        finish_date = row.find("p").getText().split(" ")[1].split(".")
                        finish_date = datetime.date(int("20"+finish_date[2]), int(finish_date[1]), int(finish_date[0]))

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

                z = requests.post("https://synrate.ru/api/offers/create",
                                  json={"name": lot_name.replace('"', ''), "location": "РФ", "home_name": "roseltorg",
                                        "offer_type": "Продажа", "offer_start_date": str(publish_date),
                                        "offer_end_date": str(finish_date),
                                        "owner": "недоступно", "ownercontact": "временно недоступно",
                                        "offer_price": lot_price,
                                        #"subcategory": "Не определена",
                                        #"category": "Не определена",
                                        "additional_data": "не указано", "organisation": organisation.replace('"', ''),
                                        "url": self.url+link})

                J = {"name": lot_name.replace('"', ''), "location": "РФ", "home_name": "roseltorg",
                                        "offer_type": "Продажа", "offer_start_date": str(publish_date),
                                        "offer_end_date": str(finish_date),
                                        "owner": "недоступно", "ownercontact": "временно недоступно",
                                        "offer_price": lot_price,
                                        #"subcategory": "Не определена",
                                        #"category": "Не определена",
                                        "additional_data": "не указано", "organisation": organisation.replace('"', ''),
                                        "url": self.url+link}

                print(f'ROSeltorg: {z.json()}  {J}')
                time.sleep(random.randint(1, 5)/10)


if __name__ == '__main__':
    parser = RoseltorgParser()
    parser.parse()
