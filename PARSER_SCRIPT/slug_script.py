import sys

from connector import conn
from pytils.translit import slugify

home_name = input('Введите источник: ')

cursor = conn.cursor()
cursor.execute(f"SELECT id, name FROM synrate_main_offer WHERE home_name = '{home_name}'")
offers = cursor.fetchall()

for offer in offers:
    try:
        id, name = offer[0], offer[1][:50]
        slug = slugify(name) + f'-{id}'
        slug = slug.replace('-', '_')

        cursor.execute(f"UPDATE synrate_main_offer SET slug = '{slug}' WHERE id = {id}")
        conn.commit()
        print(f'[+] {slug}')
    except Exception as ex:
        print('[-]', ex)
        print('id:', id)
