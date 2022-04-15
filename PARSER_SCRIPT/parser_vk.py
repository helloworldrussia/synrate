import sys
import time
import threading
from connector import conn, change_parser_status
from backend import get_api, VkGroup

lada = 'd785d6b835c25e6ab39f398b8bc010903a601ceb5f414120b4610536eb84e5856d45fc89fc577123349ac'
token = 'a77eca1a8ecf84c1ba4af75dbd5e4a500315faba4d777a7bf8c1e02e1faf9f7d396845378d89e4b13fbf7'
erick = 'c99c3ccf61df1de593411dde502690f9561696c4ce79546216a751b3a118fe94c08fe7d2ec42ba3111f0'

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


def get_vk_models():
    print(1)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM parsers_vkgroupdetail")
    all_goups = cursor.fetchall()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM parsers_vkaccount")
    all_accounts = cursor.fetchall()
    return all_goups, all_accounts


def main():
    grps, accs = get_vk_models()
    print(f'groups: {len(grps)} accounts: {len(accs)}')
    # расчитываем сколько групп будет парсить один аккаунт (экземпляр апи)
    result = len(grps) / len(accs)
    if result > int(result):
        result += 1
    result = int(result)
    print(result)
    for account in accs:
        api = get_api(account[2])
        i = 1
        list = grps[:11]
        for group in list:
            print(i)
            if i == result:
                i = 1
                break
            obj = VkGroup(group[1], group[2], group[3], api)
            th = threading.Thread(target=parse, args=(obj,))
            th.start()
            i += 1
        for x in list:
            grps.remove(x)
    print('Начинаем отслеживать потоки')
    successful = 0
    while not successful:
        if threading.active_count() <= 1:
            change_parser_status('vk.com', 'Выкл')
            sys.exit()
        print('[vk.com]Активны:', threading.active_count())
        time.sleep(3)


main()