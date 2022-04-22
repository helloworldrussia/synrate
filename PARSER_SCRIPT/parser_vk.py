import sys
import time
import threading
from connector import conn, change_parser_status
from backend import get_api, VkGroup
import vk


"""
    Необходимые для класса VkGroup данные: 
        ссылка на группу, 
        id группы в контакте, которую парсим,
        экземляр клиента (api) [передайте токен в PARSER_SCRIP.vk.backend.get_api для получения]
"""


def change_tokens_status(good, bad):
    cursor = conn.cursor()
    for x in good:
        cursor.execute(f"UPDATE parsers_vkaccount SET status = True WHERE token = '{x}'")
        conn.commit()
    for x in bad:
        cursor.execute(f"UPDATE parsers_vkaccount SET status = False WHERE token = '{x}'")
        conn.commit()


def check_tokens(data):
    good, bad = [], []
    for token in data:
        token = token[2]
        session = vk.Session(access_token=token)
        api = vk.API(session, v='5.81', lang='ru', timeout=10)
        try:
            test = api.wall.get(owner_id=-67991189, count=1)
            good.append(token)
        except:
            bad.append(token)
    change_tokens_status(good, bad)
    return good


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
    cursor.execute(f"SELECT * FROM parsers_vkaccount WHERE active = True")
    all_accounts = cursor.fetchall()
    return all_goups, all_accounts


def main():
    grps, accs = get_vk_models()
    print(f'groups: {len(grps)} accounts: {len(accs)}')
    accs = check_tokens(accs)
    # расчитываем сколько групп будет парсить один аккаунт (экземпляр апи)
    result = len(grps) / len(accs)
    if result > int(result):
        result += 1
    result = int(result)
    print(result)
    for account in accs:
        api = get_api(account)
        i = 1
        list = grps[:result]
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
# ---------------------
# api = get_api('8dbe2f8fb5e907d08fd82463d9ebf27a3f2ee828629da537549dc862302d598a3f3c695650cd3a0461fb6')
# url, id, name = 'https://vk.com/nelikvidi_com', -9203626, 'Неликвиды, оборудование, остатки | Объявления',
# obj = VkGroup(url, id, name, api)
# parse(obj)