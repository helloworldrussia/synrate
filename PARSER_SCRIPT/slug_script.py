import math
import sys
import threading

from connector import conn
from pytils.translit import slugify

"""
    Скрипт для принудительного назначения ЧПУ для заявок
    Может понадобиться при сбое в автозаполнении поля slug в модели - synrate_main.models.Offer    
"""


def main(offers, group_id):
    count = len(offers)
    i = 1
    for offer in offers:
        try:
            id, name = offer[0], offer[1][:50]
            slug = slugify(name) + f'-{id}'
            slug = slug.replace('-', '_')

            cursor.execute(f"UPDATE synrate_main_offer SET slug = '{slug}' WHERE id = {id}")
            conn.commit()
            print(f'[{group_id}] {i} / {count} {slug}')
        except Exception as ex:
            print(f'[{group_id}] {i} / {count}', ex)
            print('id:', id)
        i += 1


# home_name = input('Введите источник: ')
thr_count = int(input('Потоки?: '))

cursor = conn.cursor()
cursor.execute(f"SELECT id, name FROM synrate_main_offer WHERE slug is NULL")
offers = cursor.fetchall()

i_count = math.ceil(len(offers) / thr_count)

for x in range(1, thr_count + 1):
    group = offers[:i_count]
    offers = list(set(offers) - set(group))
    th = threading.Thread(target=main, args=(group, x,))
    th.start()