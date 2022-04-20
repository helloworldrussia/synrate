import threading
from telethon import TelegramClient
from connector import conn
from tg_backend import TelegramItem

api_id = 5355298
api_hash = '41f6f5015c036f4bae33ae51d4d7c835'
client = TelegramClient('app_synrate_session', api_id, api_hash)
client.start()


def go(client, target, target_name):
    obj = TelegramItem(client, target, target_name)
    obj.go()


def main():
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM parsers_telegramgroupdetail")
    all = cursor.fetchall()
    for group in all:
        th = threading.Thread(target=go, args=(client, group[1], group[2],))
        th.start()


main()