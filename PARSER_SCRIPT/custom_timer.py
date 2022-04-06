import datetime
import os
import threading
import time

from connector import conn


def timer():
    # time.sleep(5)
    print("TIMER: parsers autorun is ON")
    while True:
        while True:
            dt_now = datetime.datetime.now()
            time_now = dt_now.strftime("%M")
            # print(time_now)
            if time_now == "51" or time_now == "52":
            # if time_now == "00" or time_now == "01":
                change_status_for_all()
                os.system(f"python3 /var/www/synrate_dir/synrate/PARSER_SCRIPT/main.py --m short")
                time.sleep(120)
            elif datetime.datetime.today().weekday() == 5:
                change_status_for_all()
                os.system(f"python3 /var/www/synrate_dir/synrate/PARSER_SCRIPT/main.py")
            else:
                time.sleep(2)


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

timer()
# change_status_for_all()