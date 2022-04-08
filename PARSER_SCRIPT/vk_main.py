import sys
from threading import Thread

from connector import conn, change_parser_status
from backend import get_api, VkGroup

token = 'a77eca1a8ecf84c1ba4af75dbd5e4a500315faba4d777a7bf8c1e02e1faf9f7d396845378d89e4b13fbf7'

"""
    Необходимые для класса VkGroup данные: 
        ссылка на группу, 
        id группы в контакте, которую парсим,
        экземляр клиента (api) [передайте токен в PARSER_SCRIPT.vk.backend.get_api для получения]
"""


def parse(obj):
    info = obj.wall_info()
    for i in range(1, int(info['i_count'])+1):
        print(f'{i}')
        if i == 1:
            items = obj.wall_items(None)
        else:
            items = obj.wall_items(i*90)
        offers = obj.get_offers(items)
        obj.send_result(offers)
    change_parser_status('vk.com', 'Выкл')
    sys.exit()


def get_vk_group_info():
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM parsers_vkgroupdetail")
    all = cursor.fetchall()
    return all


def start_vk_parsing():
    api = get_api(token)
    all = get_vk_group_info()
    for parser in all:
        print(f'VkGroup: {parser[1]} {parser[2]} {parser[3]}')
        parser_obj = VkGroup(parser[1], parser[2], parser[3], api)
        th = Thread(target=parse, args=(parser_obj,))
        th.start()


start_vk_parsing()
