import random
import time

from ENGINE import Parser
import requests
from bs4 import BeautifulSoup
import datetime


class ParserTender(Parser):
    def __init__(self):
        super().__init__()
        self.url = "http://www.tender.pro/view_tenders_list.shtml?sid=&lim=25&companyid=0&tendertype=92&tenderstate=1&country=0&basis=0&tender_name=&tender_id=&company_name=&good_name=&dateb=&datee=&dateb2=&datee2="
        self.page_links = []
        self.page_links2 = []

    def parse(self):

        print("Tenderpro")

        self.response = requests.get(self.url.format(0), headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36"})
        self.response.encoding = 'utf-8'
        self.soup = BeautifulSoup(self.response.content, 'html.parser')
        pages = self.soup.find("div", attrs={"class": "pager"}).find_all('a')
        pages_num = pages[len(pages)-2].getText()

        for i in range(1, int(pages_num)):
            self.response = requests.get(self.url.format(i*25), headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36"})
            self.response.encoding = 'utf-8'
            self.soup = BeautifulSoup(self.response.content, 'html.parser')
            table = self.soup.find('table', attrs={"class": "baseTable"})
            rows = table.find_all('tr')

            for row in rows:
                if row.find('th') is None:
                    cols = row.find_all('td')
                    name = cols[1].find_all('a')[1].getText()
                    url = "http://www.tender.pro/"+(cols[1].find_all('a')[1]["href"])

                    created = cols[2].getText()
                    finishes = cols[3].getText()
                    company = cols[5].getText()
                    x = created.split(".")
                    start_date = datetime.date(int(x[2]), int(x[1]), int(x[0]))
                    z = finishes.split(".")
                    fin_date = datetime.date(int(z[2]), int(z[1]), int(z[0]))
                    J = {"name": name.replace('"', ''), "location": "РФ", "home_name": "tenderpro",
                                            "offer_type": "Продажа", "offer_start_date": str(start_date),
                                            "offer_end_date": str(fin_date),
                                            "owner": company.replace('"', ''), "ownercontact": "временно недоступно", "offer_price": 0,
                                            "additional_data": "не указано", "organisation": company.replace('"', ''),
                                            "url": url
                                            #"category": "Не определена", "subcategory": "не определена"
                                            }
                    z = requests.post("https://synrate.ru/api/offers/create",
                                      json=J)

                    # TESTING -------------

                    print(f'Tender-pro: {z.json()}  {J}')
                    time.sleep(random.randint(1, 5) / 10)
                    # ---------------------


if __name__ == '__main__':
    parser = ParserTender()
    parser.parse()
