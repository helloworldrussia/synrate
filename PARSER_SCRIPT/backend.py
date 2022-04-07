from datetime import datetime
import random
import time

import requests
import vk


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

    def wall_info(self):
        answer = {}
        wall = self.api.wall.get(owner_id=self.id, count=1)
        count = wall['count']
        print(count)
        i = int(count) / 90
        if i > int(i):
            i = int(i) + 1
        answer['i_count'] = i
        return answer

    def wall_items(self, offset):
        wall = self.api.wall.get(owner_id=self.id, count=90, offset=offset)
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
            text = f'Группа VK.COM: {self.name}\n{text}'
            url = self.url+f'?w=wall{self.id}_{offer["id"]}%2Fall'
            offer_obj = {"name": name,
                         "home_name": f"{self.home_name}",
                         "offer_start_date": start_date, "additional_data": text,
                         "url": url, "from_id": offer['id'], "owner_id": offer['from_id']
                         }
            answer.append(offer_obj)
        return answer

    def send_result(self, data):
        for offer in data:
            z = requests.post("https://synrate.ru/api/offers/create",
                              json=offer)
            today = datetime.today().strftime('%d-%m %H:%M')
            try:
                print(f'[{self.home_name}] {z.json()}\n{offer}')
                # with open('/var/www/synrate_dir/b2b-center.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z.json()}\n{offer}')
                #     f.close()
            except:
                print(f'[{self.home_name}] {z}\n{offer}')
                # with open('/var/www/synrate_dir/b2b-center.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z}\n{offer}')
                #     f.close()
            try:
                id = z.json()['unique_error'][0]
                z = requests.put(f"https://synrate.ru/api/offer/update/{id}/",
                                  json=offer)
            except:
                pass
            try:
                print(f'[{self.home_name}] {z.json()}\n{offer}')
                # with open('/var/www/synrate_dir/b2b-center.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z.json()}\n{offer}')
                #     f.close()
            except:
                print(f'[{self.home_name}] {z}\n{offer}')
                # with open('/var/www/synrate_dir/b2b-center.txt', 'r+') as f:
                #     # ...
                #     f.seek(0, 2)
                #     f.write(f'[{today}] {z}\n{offer}')
                #     f.close()