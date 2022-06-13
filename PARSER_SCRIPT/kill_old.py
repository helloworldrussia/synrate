import os

try:
    os.system("pkill -9 -f /var/www/synrate_dir/synrate/PARSER_SCRIPT/")
    print('- Процессы завершены.')
except Exception as ex:
    print(f'Ошибка: {ex}')