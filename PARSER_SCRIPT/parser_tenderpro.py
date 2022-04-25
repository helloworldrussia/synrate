import random
import sys
import time
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from connector import change_parser_status, Item, DbManager
from ENGINE import Parser
import requests
from bs4 import BeautifulSoup
import datetime

from mixins import proxy_data, get_proxy


class ParserTender(Parser):
    def __init__(self, end):
        super().__init__()
        self.url = "http://www.tender.pro/view_tenders_list.shtml?page={}&sid=&lim=25&companyid=0&tendertype=92&tenderstate=1&country=0&basis=0&tender_name=&tender_id=&company_name=&good_name=&dateb=&datee=&dateb2=&datee2="
        self.page_links = []
        self.page_links2 = []
        self.proxy = False
        self.current_proxy_ip = 0
        self.start_page = 0
        self.last_page = end
        self.db_manager = DbManager()

    def parse(self):
        successful = 0

        while not successful:
            time.sleep(random.randint(1, 7))
            self.soup = self.get_page_soup(self.url.format(0))
            pages = self.soup.find("div", attrs={"class": "pager"}).find_all('a')
            pages_num = pages[len(pages)-2].getText()
            successful = 1
            print(f'[tenderpro] pages count {pages_num}')

        if self.last_page:
            pages_num = int(self.last_page)
        pause_signal = 0
        for i in range(self.start_page, int(pages_num)+1):
            pause_signal += 1
            if pause_signal == 30:
                time.sleep(300)
                pause_signal = 0
            print(f"PAGE {i}", i*25)
            successful = 0
            while not successful:
                time.sleep(random.randint(1, 7))
                try:
                    self.soup = self.get_page_soup(self.url.format(25*i))
                    table = self.soup.find('table', attrs={"class": "baseTable"})
                    rows = table.find_all('tr')
                    successful = 1
                except:
                    self.change_proxy()

            for row in rows:
                if row.find('th') is None:
                    cols = row.find_all('td')
                    from_id = cols[0].getText()
                    name_obj = cols[1].find_all('a')[1]
                    name = name_obj.getText()
                    url = "http://www.tender.pro/"+name_obj.attrs['href']
                    #url = "http://www.tender.pro/"+(cols[1].find_all('a')[1]["href"])

                    created = cols[2].getText()
                    finishes = cols[3].getText()
                    company = cols[5].getText()
                    x = created.split(".")
                    start_date = datetime.date(int(x[2]), int(x[1]), int(x[0]))
                    z = finishes.split(".")
                    fin_date = datetime.date(int(z[2]), int(z[1]), int(z[0]))
                    offer = {"name": name.replace('"', ''), "location": "РФ", "home_name": "tenderpro",
                                            "offer_type": "Продажа", "offer_start_date": str(start_date),
                                            "offer_end_date": str(fin_date),
                                            "owner": company.replace('"', ''), "ownercontact": "временно недоступно", "offer_price": 0,
                                            "additional_data": "не указано", "organisation": company.replace('"', ''),
                                            "url": url, "from_id": from_id
                                            }

                    offer = Item(name, "tenderpro", url, "РФ", str(start_date), str(fin_date),
                        None, None, None, None, company.replace('"', ''), from_id,
                        None, None)
                    offer.post(self.db_manager)
                    time.sleep(random.randint(1, 5) / 10)
                    # ---------------------
            self.db_manager.task_manager()
        change_parser_status('tenderpro', 'Выкл')
        sys.exit()

    def get_page_soup(self, url):
        if self.current_proxy_ip:
            try:
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                response = session.get(url, headers={
                    'User-Agent': UserAgent().chrome}, proxies=self.proxy, timeout=5)#.content.decode("utf8")
                response.encoding = 'utf-8'
                response = response.content
            except Exception as ex:
                print('get_page_soup: не получилось сделать запрос с прокси. спим, меняем прокси и снова..',
                      f'\n{url}\n\n{ex}')
                time.sleep(2)
                return False
        else:
            response = requests.get(url, headers={'User-Agent': UserAgent().chrome}).content#.decode("utf8")
        soup = BeautifulSoup(response, 'html.parser')
        # print(response)
        return soup

    def change_proxy(self):
        print('change_proxy: start')
        self.proxy, self.current_proxy_ip = get_proxy(self.current_proxy_ip)
        time.sleep(30)


if __name__ == '__main__':
    parser = ParserTender(False)
    parser.parse()
