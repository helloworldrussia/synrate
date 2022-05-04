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


def parse_iteration(obj):
    iteration = 1
    for i in range(obj.last_i, int(obj.i_count) + 1):
        if iteration == 3:
            obj.last_i = i
            print(obj.name, 'BREAK')
            return 1
        if i == 1:
            items = obj.wall_items(None)
        else:
            items = obj.wall_items(i * 90)
        offers = obj.get_offers(items)
        # th = threading.Thread(target=obj.send_result, args=(offers,))
        # th.start()
        obj.send_result(offers)
        iteration += 1
        # time.sleep(1)


def parse(data):
    for obj in data:
        obj = obj['obj']
        info = obj.wall_info()
        time.sleep(1)
    while data != []:
        for obj in data:
            print(f"Group with", data)
            print(f"SOLDIERS:", len(data))
            parse_iteration(obj['obj'])
            if obj['obj'].thats_all:
                data.remove(obj)
    print('Z')
    change_parser_status('vk.com', 'Выкл')
    sys.exit()


def get_vk_models():
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM parsers_vkgroupdetail")
    all_goups = cursor.fetchall()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM parsers_vkaccount WHERE active = True")
    all_accounts = cursor.fetchall()
    return all_goups, all_accounts


def get_vk_group_obj_list():
    grps, accs = get_vk_models()
    accs = check_tokens(accs)

    # print(f'groups: {len(grps)} accounts: {len(accs)}')
    res = len(grps) / len(accs)

    obj_list = []

    while grps != []:
        for token in accs:
            try:
                group = grps[0]
            except:
                break
            api = get_api(token)
            obj = VkGroup(group[1], group[2], group[3], api)
            obj_list.append({"obj": obj, "token": token})
            grps.remove(group)

    # print('grps:', grps)
    return obj_list, accs


def main():
    obj_list, accs = get_vk_group_obj_list()
    for token in accs:
        soldiers = []
        for object in obj_list:
            if object['token'] == token:
                soldiers.append(object)
        # for x in soldiers:
        #     print(x)
        # print('---------')
        th = threading.Thread(target=parse, args=(soldiers,))
        th.start()
        # time.sleep(2)

    check_situation()


def check_situation():
    print('Начинаем отслеживать потоки')
    successful = 0
    while not successful:
        if threading.active_count() <= 1:
            change_parser_status('vk.com', 'Выкл')
            sys.exit()
        print('[vk.com]Активны:', threading.active_count())
        time.sleep(15)


main()