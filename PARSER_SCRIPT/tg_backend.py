import sys

import asyncio
from telethon import TelegramClient
import datetime
from telethon.tl import functions

from connector import Item

"""     Класс телеграм группы или канала.
        Для использования создайте экземпляр для канала и запустите .go()  """


class TelegramItem:
    """ Классу обязательно нужны клиент (телетон) и цель (можете использовать username) """
    def __init__(self, client, target, target_name):
        self.client = client
        self.target = target
        self.target_name = target_name
        self.limit = 100

    def go(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        successful, i = 0, 1
        # при первой итерации i = 1, и cur_id = 0
        # далее cur_id = ид последнего спаршенного сообщения
        while not successful:
            if i == 1:
                cur_id, i = 0, 2
            # получили пачку сообщений со стены
            result = self.iteration_result(cur_id)
            # отправляем результат на обработку (на сохранение уйдет оттуда)
            answer = self.data_processing(result)
            # пытаемся определить ид последнего сообщения в пачке
            # если не удалось - это последняя пачка в группе, заканчиваем работу
            try:
                cur_id = result[-1].id
                print(self.target, cur_id)
            except Exception as ex:
                print('Скачали последнюю пачку', self.target)
                successful = 1
        sys.exit()

    def iteration_result(self, cur_id):
        result = self.client(functions.messages.GetHistoryRequest(
            peer=self.target, offset_id=cur_id, offset_date=0,
            add_offset=0, limit=self.limit, max_id=0, min_id=0, hash=0,
        ))
        result = result.messages
        return result

    def data_processing(self, data):
        for offer in data:
            try:
                test = offer.message
            except :
                continue
            obj = Item(offer.message[:120], 'telegram', self.target, None, str(offer.date).split(' ')[0], None,
                       None, None, None, offer.message, None, offer.id,
                       self.target_name, offer.from_id)
            obj.post()
        return True