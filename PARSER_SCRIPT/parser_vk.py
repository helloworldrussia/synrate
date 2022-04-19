import sys
import time
import threading
from connector import conn, change_parser_status
from backend import get_api, VkGroup


"""
    Необходимые для класса VkGroup данные: 
        ссылка на группу, 
        id группы в контакте, которую парсим,
        экземляр клиента (api) [передайте токен в PARSER_SCRIP.vk.backend.get_api для получения]
"""


def parse(obj):
    # test = obj.check_connect()
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
    cursor.execute(f"SELECT * FROM parsers_vkaccount WHERE active = 1")
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