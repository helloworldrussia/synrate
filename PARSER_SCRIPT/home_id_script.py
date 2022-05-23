import math
import threading

from connector import get_home_id, conn


def validate_home_name(hn):
    if hn == 'b2b-center':
        hn = 'b2b_center'
    if hn == 'tektorg':
        hn = False
    if hn == 'nelikvidi':
        hn = 'nelikvidy'
    if hn == 'vk.com':
        hn = 'vk'
    if hn == 'etp-activ':
        hn = 'etp_aktiv'
    return hn


def main(offers, group_id):
    count = len(offers)
    print(count)
    i = 1
    for offer in offers:

        try:
            offer_id, home_name = offer[0], offer[1]
            home_name = validate_home_name(home_name)
            if not home_name:
                continue
            print(home_name)
            home_id = get_home_id(f'{home_name}')
            cursor.execute(f"UPDATE synrate_main_offer SET home_id = '{home_id}' WHERE id = {offer_id}")
            conn.commit()
            print(f'(+) [{group_id}] {i} / {count}')
        except Exception as ex:
            print(f'(!) [{group_id}] {i} / {count}', ex)
            print('id:', offer_id)
        i += 1


thr_count = int(input('Потоки?: '))

cursor = conn.cursor()
cursor.execute(f"SELECT id, home_name FROM synrate_main_offer WHERE home_id = 1")
offers = cursor.fetchall()

i_count = math.ceil(len(offers) / thr_count)

for x in range(1, thr_count + 1):
    group = offers[:i_count]
    offers = list(set(offers) - set(group))
    th = threading.Thread(target=main, args=(group, x,))
    th.start()
