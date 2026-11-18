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

В исходной конфигурации ПЗ12 именованный том не настраивался. В ПЗ13 он
добавлен; порядок переноса приведён ниже. Команды `stop` и `start` сохраняют
существующие контейнеры. Для прежней конфигурации ПЗ12 без именованного тома
сохранение данных после удаления или пересоздания не гарантировалось. Не используйте
`docker compose down -v` для этой работы.

## Постоянное хранение и сети

ПЗ13 продолжает ПЗ12 в том же проекте Compose `panainte-pz12`.
Ветвь разработки — `feature/storage-network`; она основана на
`feature/docker-compose`. PyQt6-приложение и SQL магазина сохранены.

PostgreSQL 14 хранит данные в именованном томе `db_data`, смонтированном
в `/var/lib/postgresql/data`. Фактическое имя тома при приведённых командах —
`panainte-pz12_db_data`. Сервисы `db` и `db-check` включены в пользовательскую
сеть bridge `shoe-backend` (`panainte-pz12_shoe-backend`).

### Перенос существующей базы ПЗ12

Резервную копию нужно сделать из работающей базы ПЗ12 **до** первого
применения нового `compose.yaml` с томом. Новый том не содержит таблиц из
прежнего хранилища автоматически. Если вы уже применили итоговую конфигурацию,
сначала проверьте подключённый том и наличие данных. В непустую базу повторно
не импортируйте ни дамп, ни исходный `database/shoe_store.sql` с DROP TABLE.

В корне репозитория из PowerShell (каталог `backups/` исключён из Git):

```powershell
New-Item -ItemType Directory -Force backups | Out-Null
docker compose -p panainte-pz12 run --rm db-check
docker compose -p panainte-pz12 exec db pg_dump -U shoe_user -d shoe_store -f /tmp/shoe_store_before_volume.sql
docker compose -p panainte-pz12 cp db:/tmp/shoe_store_before_volume.sql ./backups/shoe_store_before_volume.sql
Get-Item ./backups/shoe_store_before_volume.sql
```

Убедитесь, что копия существует, имеет ненулевой размер и содержит SQL.
Не публикуйте её содержимое. Храните дополнительную копию на отдельном носителе.
После проверки резервной копии добавьте монтирование тома из ПЗ13. Затем:

```powershell
docker compose -p panainte-pz12 config --quiet
docker compose -p panainte-pz12 down
docker compose -p panainte-pz12 up --build -d
docker volume ls
docker compose -p panainte-pz12 run --rm db-check
```

Перед восстановлением запросом к `information_schema.tables` проверьте,
что в новой пользовательской базе 0 таблиц. Если таблицы уже есть, остановитесь
и выясните происхождение данных; не удаляйте их автоматически. Только для
проверенного пустого целевого хранилища:

```powershell
docker compose -p panainte-pz12 cp ./backups/shoe_store_before_volume.sql db:/tmp/restore.sql
docker compose -p panainte-pz12 exec db psql -v ON_ERROR_STOP=1 -U shoe_user -d shoe_store -f /tmp/restore.sql
docker compose -p panainte-pz12 run --rm db-check
```

После восстановления этой учебной базы ожидаются 11 таблиц и 3 товара.
После добавления служебной таблицы проверки общее число таблиц станет 12.

### Проверка сохранности

```powershell
docker compose -p panainte-pz12 exec db psql -U shoe_user -d shoe_store -c "CREATE TABLE IF NOT EXISTS public.docker_persistence_check (id integer PRIMARY KEY, note text NOT NULL);"
docker compose -p panainte-pz12 exec db psql -U shoe_user -d shoe_store -c "INSERT INTO public.docker_persistence_check (id, note) VALUES (13, 'data survives recreation') ON CONFLICT (id) DO UPDATE SET note=EXCLUDED.note;"
docker compose -p panainte-pz12 exec db psql -U shoe_user -d shoe_store -c "SELECT * FROM public.docker_persistence_check;"
docker compose -p panainte-pz12 ps -q db
docker compose -p panainte-pz12 up -d --force-recreate db
docker compose -p panainte-pz12 ps
docker compose -p panainte-pz12 ps -q db
docker compose -p panainte-pz12 exec db psql -U shoe_user -d shoe_store -c "SELECT * FROM public.docker_persistence_check;"
docker compose -p panainte-pz12 run --rm db-check
```

Дождитесь `healthy` перед запросом. ID контейнера должен измениться, имя тома —
сохраниться, а строка `13 | data survives recreation` — остаться доступной.
Затем проверьте каталог командой `python main.py`.

### Адреса и диагностика сети

- В контейнере `db-check`: `DB_HOST=db`, `DB_PORT=5432`.
- В Windows, в локальном `config.ini`: `host=localhost`, `port=5433`.
- Публикация `127.0.0.1:5433:5432` ограничивает доступ к БД loopback хоста.
- У `db-check` нет опубликованных портов: это одноразовый клиент БД.

```powershell
docker compose -p panainte-pz12 config --quiet
docker compose -p panainte-pz12 up -d
docker compose -p panainte-pz12 port db 5432
docker network ls
docker network inspect panainte-pz12_shoe-backend
docker compose -p panainte-pz12 run --rm db-check
docker compose -p panainte-pz12 logs --tail=30 db-check
```

В инспекции сети должен присутствовать `db`. Одноразовый контейнер `run --rm`
удаляется после завершения, поэтому его отсутствие в списке нормально;
успешный запрос к `db:5432` подтверждает доступ между сервисами.

Для диагностики временно задайте у db-check `DB_HOST: wrong-db`: ожидаются
10 неудачных попыток и код 1. Восстановите `DB_HOST: db` и проверьте код 0.
Отдельно замените только локальный порт в `config.ini` на свободный неверный
порт, перезапустите приложение, зафиксируйте отказ соединения и верните 5433.
Не публикуйте пароль или полный вывод `docker compose config`.

### Остановка и резервные копии

`docker compose stop` останавливает существующие контейнеры.
`docker compose down` удаляет контейнеры и сети проекта, сохраняя именованный том.
Следующий `up -d` подключит тот же `db_data`.
**Не выполняйте `docker compose down -v`, `docker volume prune` или удаление
тома:** они могут уничтожить учебную базу. В этой работе они не применялись.
Именованный том защищает от обычного пересоздания контейнера, но не заменяет
резервную копию при удалении тома, повреждении данных или потере диска.

В Git исключены `.env`, `config.ini` и `backups/`. Резервный SQL-дамп также
не входит в архив исходников.
