import math
import threading

from connector import get_home_id, conn


def validate_home_name(hh):
    if hh == 'b2b-center':
        hh = 'b2b_center'
    if 'tektorg':
        hh = False
    if hh == 'nelikvidi':
        hh = 'nelikvidy'
    if hh == 'vk.com':
        hh = 'vk'
    if hh == 'etp-activ':
        hh = 'etp_aktiv'
    return hh


def main(offers, group_id):
    count = len(offers)
    i = 1
    for offer in offers:
        try:
            offer_id, home_name = offer[0], offer[1]
            home_name = validate_home_name(home_name)
            if not home_name:
                continue
            home_id = get_home_id('home_name')
            cursor.execute(f"UPDATE synrate_main_offer SET home_id = '{home_id}' WHERE id = {offer_id}")
            conn.commit()
            print(f'(+) [{group_id}] {i} / {count}')
        except Exception as ex:
            print(f'(!) [{group_id}] {i} / {count}', ex)
            print('id:', id)
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
