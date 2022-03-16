from ENGINE import Parser
import requests
from bs4 import BeautifulSoup
import datetime


class ParserTender(Parser):
    def __init__(self):
        super().__init__()
        self.url = "http://www.tender.pro/view_tenders_list.shtml?page={}&lim=25&sid=&sort=opendate_reverse&companyid=0&tenderinteresttype=&tener_invite=&tenderstate=1&tender_name=&company_name=&good_name=&datee=&dateb=&datee2=&dateb2=&tendertype=100&country=0&region=0&basis=0&tender_id=&tender_officer=1&tender_promoter=1&tender_show_own=0&tender_invited="
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
                    z = requests.post("https://synrate.ru/api/offers/create",
                                      json={"name": name, "location": "РФ", "home_name": "tenderpro",
                                            "offer_type": "Продажа", "offer_start_date": str(start_date),
                                            "offer_end_date": str(fin_date),
                                            "owner": company, "ownercontact": "временно недоступно", "offer_price": 0,
                                            "additional_data": "не указано", "organisation": company, "url": url,
                                            "category": "Не определена", "subcategory": "не определена"})


if __name__ == '__main__':
    parser = ParserTender()
    parser.parse()
