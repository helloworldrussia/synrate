import random
import time

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import unicodedata
import datetime
from ENGINE import Parser


class ParserNelikvidy(Parser):

    """
        Главный класс парсера сайта nelikvidi.com .
    """

    def __init__(self, verify):
        """
            Наследованный класс парсера. Добавленное поле verify нужно потому что у сайта сертификат протух,
             поэтому verify нужно поставить на False. Потом при необходимости не проблема вернуть обратно.
        :param verify:
        """
        super().__init__()
        self.verify = verify
        self.url = "https://nelikvidi.com"
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

    def parse(self):

        self.response = requests.get(self.url, headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36"}, verify=self.verify)
        self.response.encoding = 'utf-8'
        self.soup = BeautifulSoup(self.response.content, 'html.parser')
        uls = self.soup.find_all("ul", attrs={"class": "group-list"})
        kategories = []
        # Получение всех категорий (формат список из списков. [[ссылка, название], [ссылка, название], ..]
        for ul in uls:
            lis = ul.find_all("li")
            for li in lis:
                kategories.append([li.find("a").attrs["href"], unicodedata.normalize("NFKD", li.find("a").getText())])

        for kategory in kategories:

            self.response = requests.get(self.url+kategory[0]+'/sell', headers={'User-Agent': UserAgent().chrome},
                                         verify=self.verify)
            print(self.response, self.url+kategory[0]+'/sell')
            self.response.encoding = 'utf-8'
            self.soup = BeautifulSoup(self.response.content, 'html.parser')
            # Определение колличества страниц
            posts = int(
                unicodedata.normalize("NFKD", self.soup.find('div', attrs={"class": "summary"}).find_all("b")[1]
                                      .getText()).replace(u" ", "")
            )
            pages = posts//50
            if posts % 50 != 0:
                pages = pages+1

            if pages > 20:
                pages = 20
            for i in range(1, pages):
                self.response = requests.get(self.url+kategory[0]+"/sell/page-{}".format(self.current_page),
                                             headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36"}, verify=self.verify)
                self.soup = BeautifulSoup(self.response.content, 'html.parser')
                for link in self.soup.find_all("a", attrs={"class":"card-image"}):
                    self.post_links.append(link.attrs['href'])
                self.current_page += 1

            self.post_links = list(dict.fromkeys(self.post_links))

            # data_on_serv = requests.get("https://synrate.ru/api/offers/list")
            # for url in data_on_serv.json():
            #     try:
            #         self.post_links.remove(url["url"])
            #     except ValueError:
            #         zxc = 0

            for link in self.post_links:
                url = None
                name = None
                location = None
                offer_type = None
                offer_start_date = None
                offer_end_date = None
                offer_price = None
                owner = None
                organisation = None
                views = None
                sostoyanie = None
                amount = None
                region = None
                date = None

                self.response = requests.get(link, headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36"}, verify=self.verify)
                self.soup = BeautifulSoup(self.response.content, 'html.parser')
                try:
                    name = self.soup.find("div", attrs={"class": "section-title"}).find("h1").getText()
                except AttributeError:
                    continue

                try:
                    price = unicodedata.normalize("NFKD",
                                                  self.soup.find("span", attrs={"class": "formated_price"})
                                                  .getText().replace(u" ", "").replace(u",", ".")).strip()
                    price = round(float(price))
                except AttributeError:
                    continue

                data_paragraphs = self.soup.find_all("p")
                try:
                    organisation = self.soup.find("div", attrs={"class": "company-info"}).find("a").getText()
                except:
                    organisation = None
                for data in data_paragraphs:
                    data_type = data.find('b')
                    if data_type is not None:
                        if data_type.getText() == "Количество:":
                            amount = data.getText().replace(u"Количество:", "").strip()
                        if data_type.getText() == "Разместил:":
                            owner = data.getText().replace(u"Разместил:", "")
                            delto = data.find("a").getText()
                            owner = owner.replace(delto, "")
                            numberurl = "https://nelikvidi.com"+data.find("a")["data-url"]
                        if data_type.getText() == "Регион:":
                            region = data.getText().replace(u"Регион:", "").strip()
                        if data_type.getText() == "Тип объявления:":
                            offer_type = data.getText().replace(u"Тип объявления:", "").strip()
                        if data_type.getText() == "Состояние:":
                            sostoyanie = data.getText().replace(u"Состояние:", "").strip()
                        if data_type.getText().find('объявление размещено'):
                            try:
                                line = data.getText().replace(f"{name}- объявление размещено:", '')
                                line = line.split(' ')
                                try:
                                    year = int(line[-2].replace(',', ''))
                                    print(f'year: {year}')
                                    line.pop(-2)
                                except:
                                    year = datetime.date.today().year

                                month = line[-2].replace('.', '').replace(',', '')
                                day = line[-3]
                                month = self.monthlist[f'{month}']
                                date = datetime.date(year, int(month), int(day))
                                print(date)
                            except Exception as ex:
                                pass
                        if data_type.getText() == "Просмотров:":
                            views = data.getText().replace(u"Просмотров:", "").strip()
                if offer_type is None:
                    offer_type = "продажа"
                if date is None:
                    date = datetime.date.today()

                breadcrumb = self.soup.find("ul", attrs={"class": "breadcrumb"}).find_all("li")
                offer = {"name": name.replace('"', ''), "location": region, "home_name": "nelikvidi",
                                        "offer_type": offer_type, "offer_start_date": str(date),
                                        "owner": owner.replace('"', ''), "ownercontact": "временно недоступно", "offer_price": price,
                                        "additional_data": "не указано", "organisation": organisation.replace('"', ''), "url": link,
                                        "category": breadcrumb[1].getText().strip(),
                                        "subcategory": breadcrumb[2].getText().strip()
                                        }
                z = requests.post("https://synrate.ru/api/offers/create",
                                  json=offer)
                # ---------------------------- TESTING
                try:
                    print(z.json())
                except:
                    print(z)
                print(f"\n{link}")
                time.sleep(random.randint(1, 5) / 10)
                # ------------------------------------
            self.post_links = []


if __name__ == '__main__':
    parser = ParserNelikvidy(False)
    parser.parse()
