import configparser

import psycopg2
from psycopg2 import OperationalError

from app.paths import external_config_path


def read_db_config():
    path = external_config_path()
    config = configparser.ConfigParser(interpolation=None)
    try:
        with path.open(encoding="utf-8") as stream:
            config.read_file(stream)
        if not config.has_section("database"):
            raise ValueError("нет секции [database]")
        db = config["database"]
        required = ("host", "port", "name", "user", "password")
        missing = [key for key in required if not db.get(key, "").strip()]
        if missing:
            raise ValueError("не заполнены: " + ", ".join(missing))
        port = int(db["port"])
        if not 1 <= port <= 65535:
            raise ValueError("порт должен быть от 1 до 65535")
        return {"dbname": db["name"], "user": db["user"],
                "password": db["password"], "host": db["host"], "port": port}
    except FileNotFoundError:
        print("Не найден config.ini: " + str(path), flush=True)
        print("Создайте файл из config.ini.example рядом с EXE; "
              "при запуске исходников — в корне проекта.", flush=True)
    except (configparser.Error, OSError, UnicodeError, ValueError):
        print("Некорректный config.ini. Проверьте UTF-8, секцию [database], "
              "обязательные параметры и порт. Пароль не выводится.", flush=True)
    return None


# Сохранён экспорт для существующего модуля app.import_data.
DB_CONFIG = read_db_config()


def get_db_connection():
    if not DB_CONFIG:
        return None
    try:
        return psycopg2.connect(**DB_CONFIG, connect_timeout=3)
    except OperationalError as error:
        message = str(error).replace(DB_CONFIG["password"], "[скрыто]")
        print("Ошибка подключения к БД: " + message, flush=True)
        print("Проверьте Docker и config.ini: 127.0.0.1, опубликованный порт, "
              "имя БД, пользователь и локальный пароль.", flush=True)
        return None
