import datetime
import psycopg2


""" Подключение к БД postgres и backend сохранения заявок напрямую
    Импортируйте conn для использования соединения с базой """

conn = psycopg2.connect(
   database="synrate_db",
   user="synrate",
   password="0M3p8M1e",
   host="91.221.70.92",
   port="5432")


def change_parser_status(name, status):
   cursor = conn.cursor()
   cursor.execute(f"UPDATE synrate_main_parserdetail SET status = '{status}' WHERE name = '{name}'")
   conn.commit()


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
      # для заявок с вк
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
      if self.home_name == 'tenderpro':
         group = self.get_db_data("synrate_main_offer", 'name', 'home_name', "= 'tenderpro'", False, False)
         for item in group:
            if item[0] == self.name:
               return False, 'Tenderpro validation failed. Not unique'

      if self.owner_id:
         group = self.get_db_data("synrate_main_offer", 'additional_data', 'owner_id', f"= '{self.owner_id}'", False, False)
         for item in group:
            if item[0] == self.additional_data:
               return False, 'VK validation failed. Not unique'

      else:
         group = self.get_db_data("synrate_main_offer", 'name', 'url', f"= '{self.url}'", False, False)
         for item in group:
            if item[0] == self.name:
               return False, 'Validation failed. Not unique offer'

      return True, 'OK'

   def get_db_data(self, table, target, field, value, second_field, second_value):
      cursor = self.conn.cursor()
      if second_field:
         try:
            cursor.execute(f"SELECT {target} FROM {table} WHERE {field} {value} AND {second_field} {second_value}")
         except:
            self.conn.rollback()
         qs = cursor.fetchall()
         return qs
      try:
         cursor.execute(f"SELECT {target} FROM {table} WHERE {field} {value}")
      except:
         self.conn.rollback()
      qs = cursor.fetchall()
      return qs
# ------------------
# name, home_name, url, location = 'Тросостойка П4', 'tenderpro', 'https://reserve.isource.ru/trades/item/trosostojka-p43-50068', 'РФ'
# offer_start_date, offer_end_date = '2022-06-06', '2022-07-07'
# owner, ownercontact, offer_price, additional_data, organisation = 'Антонов В. А.', 'Антонов В. А.', 777, name, 'ОАО'
# created_at, from_id, short_cat, owner_id = datetime.datetime.now(), '18233377', 'some_short_cat', None
#
# data = {"name": name, "home_name": home_name, "url": url, "location": location,
# "offer_start_date": offer_start_date, "offer_end_date": offer_end_date, "owner": owner, "ownercontact": ownercontact,
# "offer_price": offer_price, "additional_data": additional_data, "organisation": organisation,
# "from_id": from_id, "short_cat": short_cat, "owner_id": owner_id}
#
# obj = Item(**data)
# obj.post()
# a = Offer.objects.filer(home_name='vk.com')
# print(a)
# res = obj.get_db_data("synrate_main_offer", 'name', 'home_name', "= 'tenderpro'", False, False)
# print('result', len(res), res)
# i = 1
# for x in res:
#    print(i, x)
#    i += 1
# ------------------