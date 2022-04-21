import os
import threading
from connector import conn

""" Диспетчер всех парсеров, запустите скрипт для начала работы.
    Для полного цикла парсеров сайтов-источников можно запустить скрипт main.py 
    TG main - telegram.py 
    VK main - parser_vk
    www-main - main.py """
# телеграм временно запускается отдельно из-за проблем с автоматической авторизацией
# при работе через cron


def start_default(mode):
    os.system(f"python3 /var/www/synrate_dir/synrate/PARSER_SCRIPT/main.py{mode}")


def start_vk():
    os.system(f"python3 /var/www/synrate_dir/synrate/PARSER_SCRIPT/parser_vk.py")


# def start_tg():
#     os.system(f"python3 /var/www/synrate_dir/synrate/PARSER_SCRIPT/telegram")


def start():
    change_status_for_all()

    th = threading.Thread(target=start_default, args=(' --m short',))
    th.start()

    th_vk = threading.Thread(target=start_vk)
    th_vk.start()

    # th_tg = threading.Thread(target=start_tg)
    # th_tg.start()

    th.join()
    th_vk.join()
    # th_tg.join()


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