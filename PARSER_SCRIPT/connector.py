# -*- coding: utf-8 -*-
import datetime
import time

import psycopg2
from dateutil.relativedelta import relativedelta

""" Импортируйте conn для использования соединения с базой """

conn = psycopg2.connect(
   database="synrate_db",
   user="synrate",
   password="0M3p8M1e",
   host="91.221.70.92",
   port="5432")


def save_from_id(id, db):
   try:
      cursor = conn.cursor()
      cursor.execute(f"INSERT INTO {db}(from_id) VALUES({id})")
      conn.commit()
   except:
      conn.rollback()


def change_parser_status(name, status):
   cursor = conn.cursor()
   cursor.execute(f"UPDATE synrate_main_parserdetail SET status = '{status}' WHERE name = '{name}'")
   conn.commit()


""" Класс заявки для сохранения напрямую в БД.
    Вводите данные при создании экз. класса, если какого-то парметра от парсера не поступает, вписывайте None """


class Item:

   def __init__(self, name, home_name, url, location, offer_start_date, offer_end_date,
                owner, ownercontact, offer_price, additional_data, organisation, from_id,
                short_cat, owner_id):
      self.conn = conn
      self.name = name
      self.home_name = home_name
      self.location = location
      self.url = url
      self.offer_start_date = offer_start_date
      self.offer_end_date = offer_end_date
      self.owner = owner
      self.ownercontact = ownercontact
      self.offer_price = offer_price
      self.additional_data = additional_data
      self.organisation = organisation
      self.created_at = datetime.datetime.now()
      self.from_id = from_id
      # для заявок с вк и тг
      self.short_cat = short_cat
      self.owner_id = owner_id
      self.views = 1
      self.arg_list = {"owner_id": self.owner_id, "short_cat": self.short_cat, "from_id": self.from_id,
                     "created_at": self.created_at, "organisation": self.organisation,
                     "additional_data": self.additional_data,
                     "offer_price": self.offer_price, "ownercontact": self.ownercontact,
                     "owner": self.owner, "offer_end_date": self.offer_end_date, "offer_start_date": self.offer_start_date,
                     "url": self.url, "location": self.location,
                     "home_name": self.home_name, "name": self.name, "views": self.views}

   def post(self):
      successful, message = self.validate()
      print(f'[{self.home_name}]', successful, message)
      if successful:
         arg_string = ''
         val_string = ''
         for key, value in self.arg_list.items():
            if self.arg_list[f'{key}'] is not None and self.arg_list[f'{key}'] != '':
               arg_string += f'{key},'
               val_string += f"'{self.arg_list[f'{key}']}',"
            else:
               if key == 'offer_start_date':
                  custom_start_date = one_month = datetime.date.today() + relativedelta(months=-1)
                  arg_string += f'offer_start_date,'
                  val_string += f"'{custom_start_date}',"
         arg_string, val_string = arg_string[:-1], val_string[:-1]
         cursor = self.conn.cursor()
         try:
            cursor.execute(f"INSERT INTO synrate_main_offer "
                           f"({arg_string}) "
                           f"VALUES({val_string})")
            self.conn.commit()
            return True
         except:
            self.conn.rollback()
      return False

   def validate(self):

      if self.name == '' or self.name is None:
         return False, 'Failed name validation'

      if self.home_name == 'tenderpro':
            group = self.get_db_data("synrate_main_offer", 'name', 'home_name', "= 'tenderpro'", False, False)
            if group:
               for item in group:
                  if item[0] == self.name:
                     return False, 'Tenderpro validation failed. Not unique'
      if self.owner_id:
            group = self.get_db_data("synrate_main_offer", 'additional_data', 'owner_id', f"= '{self.owner_id}'", False, False)
            if group:
               for item in group:
                  if item[0] == self.additional_data:
                     return False, 'VK/TG validation failed. Not unique'
            if self.home_name == 'telegram':
               save_from_id(self.owner_id, 'synrate_main_tguser')
            elif self.home_name == 'vk.com':
               save_from_id(self.owner_id, 'synrate_main_vkuser')

      else:
            group = self.get_db_data("synrate_main_offer", 'name', 'url', f"= '{self.url}'", False, False)
            if group:
               for item in group:
                  if item[0] == self.name:
                     return False, 'Validation failed. Not unique offer'
      return True, 'OK'

   def get_db_data(self, table, target, field, value, second_field, second_value):
      cursor = self.conn.cursor()
      if second_field:
         try:
            cursor.execute(f"SELECT {target} FROM {table} WHERE {field} {value} AND {second_field} {second_value}")
            qs = cursor.fetchall()
         except:
            self.conn.rollback()
            qs = 0
         return qs
      try:
         cursor.execute(f"SELECT {target} FROM {table} WHERE {field} {value}")
         qs = cursor.fetchall()
      except:
         self.conn.rollback()
         qs = 0
      return qs

a = '''🛺🚨Добрый день! Москва и МО Предлагаем услуги по перевозке бригад, грузов на коммерческом транспорте: Аренда Газель ферме 🛺🚨Добрый день! Москва и МО Предлагаем услуги по перевозке бригад, грузов на коммерческом транспорте: Аренда Газель фермер 5+1 (тент), Мерседес спринтер 2+1 (фургон), Соболь 6+1 (фургон). Форма оплаты любая: ИП, ООО. Сергей 84955818888 89646313884'''
item = Item(a, 'telegram', 'test:test.com', None, None, None,
                None, None, None, a, None, 111111,
                None, 13131313)
print(item.name)
print(item.additional_data)
item.post()
