from datetime import datetime
import random
import time

import requests
import vk

from PARSER_SCRIPT.connector import Item


def get_api(token):
    session = vk.Session(access_token=token)
    api = vk.API(session, v='5.81', lang='ru', timeout=10)
    return api


class VkGroup:
    def __init__(self, url, id, name, api):
        self.id = id
        self.api = api
        self.home_name = 'vk.com'
        self.url = url
        self.name = name

    def check_connect(self):
        wall = self.api.wall.get(owner_id=self.id, count=1)
        print(wall)

    def wall_info(self):
        answer = {}
        successful = 0
        while not successful:
            try:
                wall = self.api.wall.get(owner_id=self.id, count=1)
                successful = 1
            except Exception as ex:
                print(ex)
                time.sleep(random.randint(1, 3))
        count = wall['count']
        print(count)
        i = int(count) / 90
        if i > int(i):
            i = int(i) + 1
        answer['i_count'] = i
        return answer

    def wall_items(self, offset):
        successful = 0
        while not successful:
            try:
                wall = self.api.wall.get(owner_id=self.id, count=90, offset=offset)
                successful = 1
            except:
                time.sleep(random.randint(1, 3))
        wall_items = wall['items']
        return wall_items

    def get_offers(self, data):
        answer = []
        ids = []
        for offer in data:
            if offer['text'] is None or offer['text'] == '':
                continue
            name, text = offer['text'], offer['text']
            name = name[:120]
            start_date = datetime.utcfromtimestamp(int(offer['date'])).strftime('%Y-%m-%d')
            ids.append(offer['from_id'])
            url = self.url+f'?w=wall{self.id}_{offer["id"]}%2Fall'
            offer_obj = {"name": name, "short_cat": self.name,
                         "home_name": f"{self.home_name}",
                         "offer_start_date": start_date, "additional_data": text,
                         "url": url, "from_id": offer['id'], "owner_id": offer['from_id']
                         }
            offer = Item(name, self.home_name, url, None, None, None,
                None, None, None, text, None, offer['id'],
                self.name, offer['from_id'])
            answer.append(offer)
        return answer

    def send_result(self, data):
        i = 0
        for offer in data:
            offer.post()
            # if i == 5:
            #     time.sleep(1)
            #     i = 0


lada = 'd785d6b835c25e6ab39f398b8bc010903a601ceb5f414120b4610536eb84e5856d45fc89fc577123349ac'
token = 'a77eca1a8ecf84c1ba4af75dbd5e4a500315faba4d777a7bf8c1e02e1faf9f7d396845378d89e4b13fbf7'
erick = 'c99c3ccf61df1de593411dde502690f9561696c4ce79546216a751b3a118fe94c08fe7d2ec42ba3111f0'

# api = get_api(lada)
# api_ = get_api(lada)
#
# first = VkGroup('https://test.com', -67991189, 'first', api)
# second = VkGroup('https://test.com', -67991189, 'second', api_)
#
# for x in range(1,  100):
#     print(first.wall_items(x))