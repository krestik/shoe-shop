import configparser
import os

import psycopg2
from psycopg2 import OperationalError

# Параметры подключения читаются из config.ini (файл не попадает в репозиторий).
# Образец с вымышленными значениями лежит в config.ini.example.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, "config.ini"), encoding="utf-8")
_db = config["database"]

DB_CONFIG = {
    "dbname": _db["name"],
    "user": _db["user"],
    "password": _db["password"],
    "host": _db["host"],
    "port": _db["port"],
}


def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except OperationalError as e:
        print(
            f"Ошибка подключения к БД: {e}\n"
            "Проверьте настройки в config.ini: хост, порт, имя базы, пользователь и пароль.\n"
            "Если файла config.ini нет, создайте его из образца config.ini.example."
        )
        return None
