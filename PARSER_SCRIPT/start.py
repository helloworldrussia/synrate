import os
import threading

from mixins import get_all_proxies, check_proxy
from connector import conn

""" Диспетчер всех парсеров, запустите скрипт для начала работы.
    Для полного цикла парсеров сайтов-источников можно запустить скрипт main.py 
    TG main - telegram.py 
    VK main - parser_vk
    www-main - main.py """


def start_default(mode):
    os.system(f"python3 /var/www/synrate_dir/synrate/PARSER_SCRIPT/main.py{mode}")


def start_vk():
    os.system(f"python3 /var/www/synrate_dir/synrate/PARSER_SCRIPT/parser_vk.py")


# def start_tg():
#     os.system(f"python3 /var/www/synrate_dir/synrate/PARSER_SCRIPT/telegram")

def update_proxy_info(proxy_list: list):
    print('#### PROXY AUTO-CHECKER ON ####')
    bad, good = [], []
    cursor = conn.cursor()
    for proxy in proxy_list:
        ip = proxy['https'].split('@')[1].split(':')[0]
        check_res = check_proxy(proxy)
        cursor.execute(f"UPDATE parsers_proxy SET status = {check_res} WHERE ip = '{ip}'")
        conn.commit()
        print(ip, check_res)
    print('#### PROXY AUTO-CHECKER OFF ####')
    print('More info on synrate.ru admin page')


def start():
    print('... Запуск программы ...')
    print("Убиваем старые процессы...")
    try:
        os.system("pkill -9 -f /var/www/synrate_dir/synrate/PARSER_SCRIPT/")
        print('- Процессы завершены.')
    except Exception as ex:
        print(f'Ошибка: {ex}')
    change_status_for_all()
    print('- Статусы парсеров обновлены')
    proxy_list = get_all_proxies()
    update_proxy_info(proxy_list)
    print('- Проверка прокси завершена, приступаем к работе')
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