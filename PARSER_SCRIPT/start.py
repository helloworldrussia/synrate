import datetime
import os
import threading
import time

from connector import conn


def start_default(mode):
    os.system(f"python3 /var/www/synrate_dir/synrate/PARSER_SCRIPT/main.py{mode}")


def start_vk():
    os.system(f"python3 /var/www/synrate_dir/synrate/PARSER_SCRIPT/vk_main.py")


def start():
    change_status_for_all()
    th = threading.Thread(target=start_default, args=(' --m short',))
    th.start()
    th_second = threading.Thread(target=start_vk)
    th_second.start()
    th.join()
    th_second.join()


def change_status_for_all():
    # меняет статусы всех парсеров на "В работе". При включении.
    # Смена статуса на "Выкл" происходит каждым парсером самостоятельно из файла с парсером.
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM synrate_main_parserdetail")
    names = cursor.fetchall()
    for name in names:
        name = name[0]
        cursor.execute(f"UPDATE synrate_main_parserdetail SET status = 'В работе' WHERE name = '{name}'")
        conn.commit()

start()
# change_status_for_all()