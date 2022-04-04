import psycopg2

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
   # conn.close()