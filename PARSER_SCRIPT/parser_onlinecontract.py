from ENGINE import Parser
import requests
from bs4 import BeautifulSoup

class ParserOnlineContract(Parser):
    def __init__(self):
        super.__init__
        self.url = "https://onlinecontract.ru/tenders?limit=100&page={}"
        self.procedure_id = None
        self.response_item = None

    def parse(self):
        for i in range(100):
            self.response = requests.get(self.url.format(i), headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"}, verify=False).content. \
                decode("utf8")
            self.soup = BeautifulSoup(self.response, 'html.parser')
            self.post_links = self.soup.find_all("a", attrs={"class": "g-color-black"})
            self.post_links = list(set(self.post_links))
            for post in self.post_links:
                self.procedure_id = post["href"].split("/")[2].split("?")[0]
                self.response_item = requests.get(
                    "https://api.onlc.ru/purchases/v1/public/procedures/{}/positions".format(self.procedure_id),
                    headers={'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"}, verify=False
                ).json()["data"][0]
                try:
                    date = self.response_item["OwnerSklad"].split(".")[2] + "-" + self.response_item["OwnerSklad"].split(".")[1] + "-" + self.response_item["OwnerSklad"].split(".")[0]
                except:
                    date = None

                z = requests.post("https://synrate.ru/api/offers/create",
                                  json={"name": self.response_item["Name"],
                                        "location": None,
                                        "home_name": "onlinecontract",
                                        "offer_type": "Продажа",
                                        "offer_start_date": None,
                                        "offer_end_date": date,
                                        "owner": None,
                                        "ownercontact": None,
                                        "offer_price": int(float(self.response_item["Price"])),
                                        "additional_data": self.response_item["OwnerCondi"],
                                        "organisation": None,
                                        "url": "https://api.onlc.ru/purchases/v1/public/procedures/{}/positions".format(self.procedure_id),
                                        "category": "Не определена", "subcategory": "не определена"
                                        }
                                  )



if __name__ == '__main__':
    Parser = ParserOnlineContract()
    Parser.parse()
