# ShoeShop — система просмотра каталога и оформления заказов обуви

Учебный проект: десктопное приложение (Python, PyQt6) для просмотра каталога
обуви и оформления заказов с базой данных PostgreSQL.

## Возможности
- просмотр каталога моделей обуви с ценой, скидкой и наличием;
- сортировка, фильтрация и поиск товаров;
- оформление заказа авторизованным пользователем;
- управление товарами и заказами (менеджер и администратор);
- вход в систему по логину и паролю или в режиме гостя.

## Требования
- Python 3.10
- PostgreSQL 14
- библиотеки из файла requirements.txt

## Установка и запуск
1. Клонировать репозиторий: `git clone https://github.com/krestik/shoe-shop.git`
2. Создать окружение и установить зависимости:
   `python -m venv venv`, `venv\Scripts\activate`, `pip install -r requirements.txt`
3. Создать базу данных `shoe_store` и загрузить скрипт `database/shoe_store.sql`.
4. Скопировать `config.ini.example` в `config.ini` и указать параметры подключения.
5. (Необязательно) Заполнить базу демо-данными из Excel: `python -m app.import_data`.
6. Запустить приложение: `python main.py`

## Структура репозитория
- `main.py` — точка входа приложения
- `app/` — модули приложения (подключение к БД, импорт данных, формы интерфейса)
- `resources/` — изображения товаров, логотип, иконка
- `database/` — скрипт базы данных
- `import_files/` — данные для импорта (Excel)
- `docs/` — ER-диаграмма

## ER-диаграмма базы данных
Файл диаграммы: `docs/er_diagram.pdf`.

Диаграмма отражает структуру базы данных `shoe_store` (скрипт — `database/shoe_store.sql`).
Основные таблицы:
- `Role` — роли пользователей (администратор, менеджер, клиент);
- `User` — пользователи системы, связь с ролью;
- `ProductCategory`, `ProductManufacturer`, `ProductSupplier`, `ProductUnit` — справочники товаров;
- `Product` — товары каталога (артикул, цена, скидка, количество на складе);
- `OrderStatus`, `PickupPoint` — статусы заказов и пункты выдачи;
- `Order` — заказы клиентов;
- `OrderProduct` — состав заказа (связь «многие ко многим» между заказами и товарами).

## Автор
Панаинте Василий Семенович, группа ПКС-42

## Запуск PostgreSQL через Docker Compose

GUI магазина (PyQt6) работает в Windows. В Linux-контейнерах запускаются
PostgreSQL 14 и одноразовый диагностический сервис `db-check`.
Нужны Docker Desktop с запущенным Linux Engine, современный плагин Compose
и установленные зависимости Windows-приложения из `requirements.txt`.

### Настройка

В PowerShell из корня репозитория:

```powershell
Copy-Item .env.example .env
```

В локальном `.env` замените `POSTGRES_PASSWORD` своим учебным паролем.
Не добавляйте `.env` и `config.ini` в Git. Порт Windows по умолчанию — 5433.
Затем выполните:

```powershell
docker compose -p panainte-pz12 config --quiet
docker build -t shoe-shop-db-check:1.0 ./docker/db-check
docker compose -p panainte-pz12 up --build -d
docker compose -p panainte-pz12 ps --all
docker compose -p panainte-pz12 run --rm db-check
```

`db` должен стать `healthy`; `db-check` завершается с кодом 0 и выводит имя БД
и число таблиц. До импорта ожидается 0 таблиц.

### Первый импорт в пустую учебную БД

Исходный `database/shoe_store.sql` содержит `DROP TABLE`. Выполняйте его
только в новой пустой учебной базе: повторный импорт удаляет прежние таблицы.
Для существующей базы сначала требуется отдельная резервная копия и анализ
необходимых изменений. В скрипте нет исполняемых `CREATE DATABASE` и `\connect`.

```powershell
docker compose -p panainte-pz12 cp database/shoe_store.sql db:/tmp/shoe_store.sql
docker compose -p panainte-pz12 exec db psql -v ON_ERROR_STOP=1 -U shoe_user -d shoe_store -f /tmp/shoe_store.sql
docker compose -p panainte-pz12 run --rm db-check
```

Для предоставленного SQL после импорта диагностический сервис видит 11 таблиц.

### Подключение Windows-приложения

Скопируйте `config.ini.example` в `config.ini`. Укажите `host=localhost`,
`port=5433`, `name=shoe_store`, `user=shoe_user` и тот же локальный пароль,
что в `.env`. Затем:

```powershell
python main.py
```

Внутри Compose сервис `db-check` использует `DB_HOST=db` и `DB_PORT=5432`:
`localhost` внутри контейнера относится к самому контейнеру, а не к Windows.
Если 5433 занят, выберите другой `POSTGRES_HOST_PORT` в `.env` и тот же порт
в локальном `config.ini`.

### Диагностика и остановка

```powershell
docker compose -p panainte-pz12 logs --tail=40 db
docker compose -p panainte-pz12 logs --tail=30 db-check
docker compose -p panainte-pz12 stop
docker compose -p panainte-pz12 start
docker compose -p panainte-pz12 run --rm db-check
```

Для учебной ошибки временно замените `DB_HOST: db` на `DB_HOST: wrong-db`,
запустите одноразовую проверку и убедитесь, что она возвращает код 1. Затем
восстановите `DB_HOST: db` и повторите проверку: ожидается код 0.

Именованный том намеренно не настроен: это тема ПЗ13. Команды `stop` и `start`
сохраняют существующие контейнеры. Гарантировать сохранение данных после их
удаления или пересоздания в этой конфигурации нельзя. Не используйте
`docker compose down -v` для этой работы.
