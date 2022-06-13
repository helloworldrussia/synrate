import datetime
import sys
import threading
import time
from pytils.translit import slugify

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


def get_home_id(home_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM synrate_main_parserdetail WHERE name = '{home_name}'")
    home_id = cursor.fetchone()[0]
    return home_id


class DbManager:

    def __init__(self):
        self.conn = conn

        self.tasks = []

    def task_manager(self):
        if self.tasks != []:
            if self.do_tasks():
                return True

    def do_tasks(self):
        while self.tasks != []:
            cur_task = self.tasks[0]
            self.tasks.remove(cur_task)
            self.post(cur_task)
        return True

    def post(self, obj):
        successful, message = self.validate(obj)
        print(f'[{obj.home_name}]', successful, message)
        if successful:
            succ = 0
            arg_string, val_string = self.get_strs(obj)
            cursor = self.conn.cursor()
            while not succ:
                try:
                    cursor.execute(f"INSERT INTO synrate_main_offer "
                                   f"({arg_string},active) "
                                   f"VALUES({val_string},false) RETURNING id")
                    offer_id = cursor.fetchone()[0]
                    self.conn.commit()
                    self.add_slug(obj, offer_id)
                    succ = 1
                except Exception as ex:
                    print(ex)
                    # self.conn.rollback()
                    time.sleep(0.3)
        return True

    def add_slug(self, obj, offer_id):
        slug = slugify(obj.name[:50]) + f'-{offer_id}'
        slug = slug.replace('-', '_')

        cursor = self.conn.cursor()
        successful = 0
        while not successful:
            try:
                cursor.execute(f"UPDATE synrate_main_offer SET slug = '{slug}', active = true WHERE id = '{offer_id}'")
                self.conn.commit()
                successful = 1
                print(f'Заявка {offer_id} | {slug} сохранена')
            except Exception as ex:
                print(ex)
                cursor.execute('END TRANSACTION;')
                print(f"{offer_id} slug fail")
                time.sleep(0.4)

    @staticmethod
    def get_strs(obj):
        arg_string = ''
        val_string = ''
        for key, value in obj.arg_list.items():
            if obj.arg_list[f'{key}'] is not None and obj.arg_list[f'{key}'] != '' and obj.arg_list[f'{key}'] != ' \
                                                                                                                 ':
                arg_string += f'{key},'
                val_string += f"'{obj.arg_list[f'{key}']}',"
            else:
                if key == 'offer_start_date':
                    custom_start_date = one_month = datetime.date.today() + relativedelta(months=-1)
                    arg_string += f'offer_start_date,'
                    val_string += f"'{custom_start_date}',"
                else:
                    arg_string += f'{key},'
                    val_string += f"NULL,"

        return arg_string[:-1], val_string[:-1]

    def validate(self, obj):
        if obj.name == '' or obj.name is None:
            return False, 'Failed name validation'

        if obj.home_name == 'tenderpro':
            group = self.get_db_data("synrate_main_offer", 'name', 'home_name', "= 'tenderpro'", False, False)
            if group:
                for item in group:
                    if item[0] == obj.name:
                        return False, 'Tenderpro validation failed. Not unique'
            elif group == []:
                pass
            elif group == 0:
                return False, 'Validation SELECT FROM failed'

        if obj.owner_id:
            group = self.get_db_data("synrate_main_offer", 'additional_data', 'owner_id', f"= '{obj.owner_id}'", False,
                                     False)
            if group:
                for item in group:
                    if item[0] == obj.additional_data:
                        return False, 'VK/TG validation failed. Not unique'
            elif group == []:
                pass
            elif group == 0:
                return False, 'Validation SELECT FROM failed'

            if obj.home_name == 'telegram':
                save_from_id(obj.owner_id, 'synrate_main_tguser')
            elif obj.home_name == 'vk.com':
                save_from_id(obj.owner_id, 'synrate_main_vkuser')

        else:
            group = self.get_db_data("synrate_main_offer", 'name', 'url', f"= '{obj.url}'", False, False)
            if group:
                for item in group:
                    if item[0] == obj.name:
                        return False, 'Validation failed. Not unique offer'
            elif group == []:
                pass
            elif group == 0:
                return False, 'Validation SELECT FROM failed'

        return True, 'OK'

    def get_db_data(self, table, target, field, value, second_field, second_value):
        cursor = self.conn.cursor()
        if second_field:
            try:
                cursor.execute(f"SELECT {target} FROM {table} WHERE {field} {value} AND {second_field} {second_value}")
                qs = cursor.fetchall()
            except Exception as ex:
                print(ex)
                cursor.execute('END TRANSACTION;')
                # self.conn.rollback()
                time.sleep(0.2)
                qs = 0
            return qs
        try:
            cursor.execute(f"SELECT {target} FROM {table} WHERE {field} {value}")
            qs = cursor.fetchall()
        except Exception as ex:
            print(ex)
            # self.conn.rollback()
            cursor.execute('END TRANSACTION;')
            time.sleep(0.2)
            qs = 0
        return qs


# db_manager = DbManager()


class Item:

    def __init__(self, name, home_name, url, location, offer_start_date, offer_end_date,
                 owner, ownercontact, offer_price, additional_data, organisation, from_id,
                 short_cat, owner_id, home_id):
        self.home_id = home_id
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
        data = {"owner_id": self.owner_id, "short_cat": self.short_cat, "from_id": self.from_id,
                "created_at": self.created_at, "organisation": self.organisation,
                "additional_data": self.additional_data,
                "offer_price": self.offer_price, "ownercontact": self.ownercontact,
                "owner": self.owner, "offer_end_date": self.offer_end_date,
                "offer_start_date": self.offer_start_date,
                "url": self.url, "location": self.location,
                "home_name": self.home_name, "name": self.name, "views": 1, "home_id": self.home_id}
        self.arg_list = self.refactor_items_data(data)

    @staticmethod
    def refactor_items_data(data):
        attrs = ['name', 'location', 'owner', 'ownercontact',
                 'additional_data', 'organisation', 'short_cat']
        for key in attrs:
            try:
                data[key] = data[key].replace("'", "").replace('"', '')
            except:
                pass
        return data

    def post(self, db_manager):
        db_manager.tasks.append(self)
