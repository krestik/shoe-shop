# Установка и запуск ShoeStore

Комплект предназначен для Windows 10/11 x64. Приложение создано в Windows
на Python 3.10.11, PyQt6 6.10.2 и PyInstaller 6.22.3, в режиме onedir с консолью.
Для запуска комплекта Python, pip и IDE не нужны. Docker Desktop с Linux
containers и Docker Compose нужны отдельно: PostgreSQL не встроен в EXE.
На другом компьютере проверка не выполнялась; перенос в другую папку на этом
Windows-компьютере не доказывает совместимость со всеми версиями Windows.

## Состав и распаковка

Распакуйте ZIP целиком в доступную для записи папку, например Documents.
Не переносите один EXE: каталог `application/ShoeStore/_internal` содержит
интерпретатор, Qt, плагины, библиотеки и ресурсы. Не запускайте EXE прямо из ZIP.

- `application/ShoeStore/ShoeStore.exe` и вся папка `_internal` — приложение;
- `deployment/compose.yaml`, `deployment/.env.example` и `deployment/docker/db-check/`
  — серверная инфраструктура и контекст сборки диагностического сервиса;
- `deployment/database/shoe_store.sql` — исходный учебный SQL для новой пустой БД;
- `config.ini.example`, `README.md`, `INSTALL.md` — шаблон и инструкции.

## Подготовка PostgreSQL

Откройте PowerShell в `deployment`. Проверьте, что порт 5433 свободен или уже
занят именно нужным экземпляром этого учебного проекта. Если продолжаете ПЗ13,
используйте прежние `.env`, пароль, имя проекта `panainte-pz12` и том
`panainte-pz12_db_data`. Не инициализируйте заполненную базу повторно.

Для нового развёртывания:

```powershell
Copy-Item .env.example .env
```

В локальной `.env` замените `POSTGRES_PASSWORD` своим паролем. Пароль не должен
оставаться равным заглушке. Затем:

```powershell
docker compose -p panainte-pz12 config --quiet
docker compose -p panainte-pz12 up --build -d
docker compose -p panainte-pz12 ps --all
docker compose -p panainte-pz12 run --rm db-check
```

Ожидается `db: running/healthy`. `db-check` — одноразовый клиент; `Exited (0)`
означает успех, а не сбой. Внутри сети используется адрес `db:5432`, в Windows —
`127.0.0.1:5433`. Том и сеть из ПЗ13 сохранены.

### Первый импорт только в новую пустую базу

Сначала проверьте число пользовательских таблиц:

```powershell
docker compose -p panainte-pz12 exec db psql -U shoe_user -d shoe_store -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
```

Если результат не 0, остановитесь: в базе уже есть данные. Для продолжаемой
ПЗ13 ожидаются 12 таблиц, включая `docker_persistence_check`; импорт не нужен.
Если результат 0 и вы убедились, что это новая учебная база:

```powershell
docker compose -p panainte-pz12 cp database/shoe_store.sql db:/tmp/shoe_store.sql
docker compose -p panainte-pz12 exec db psql -v ON_ERROR_STOP=1 -U shoe_user -d shoe_store -f /tmp/shoe_store.sql
docker compose -p panainte-pz12 run --rm db-check
```

Скрипт содержит `DROP TABLE` и вымышленные учебные учётные записи. Повторный
импорт удаляет прежние таблицы магазина. Для существующих данных сначала нужна
отдельная резервная копия и решение о переносе. После первого импорта ожидаются
11 таблиц и 3 товара. Контрольная служебная таблица ПЗ13 не нужна для обычного
пользовательского запуска.

## Внешняя конфигурация приложения

Из корня распакованного комплекта:

```powershell
Copy-Item config.ini.example application/ShoeStore/config.ini
```

Отредактируйте созданный файл:

```ini
[database]
host = 127.0.0.1
port = 5433
name = shoe_store
user = shoe_user
password = ваш_локальный_пароль_из_env
```

Путь к файлу — рядом с `ShoeStore.exe`, а не внутри `_internal` и не относительно
текущей директории PowerShell. Изменения настроек вступают в силу при следующем
запуске приложения, пересборка EXE не нужна. Если порт изменён в `.env`, укажите
тот же опубликованный порт в `config.ini`. Не пересылайте реальные `.env` и
`config.ini` вместе с учебным архивом.

## Запуск и проверка

```powershell
& ./application/ShoeStore/ShoeStore.exe
```

Откройте режим гостя и проверьте 3 товара, цены и остатки. У одного товара в
исходном SQL есть фотография; для двух без фотографии показывается явная
заглушка «Нет фотографии». Логотипы и все пять UI-форм входят в комплект.
Добавленные пользователем фотографии сохраняются рядом с EXE в `user-resources`,
а поставляемые ресурсы остаются в `_internal/resources`.

Для отдельной автоматической проверки ресурсов и базы можно использовать:

```powershell
& ./application/ShoeStore/ShoeStore.exe --self-check ./check-output
```

Команда создаёт локальный JSON-протокол и изображения настоящих виджетов Qt,
читает товары без изменения БД и возвращает 0 при успешной проверке. Полная
учебная проверка ожидает сохранённую служебную запись ПЗ13 `id=13`; при новом
развёртывании без этой записи используйте обычный запуск и `db-check`.
Автоматическая проверка не заменяет ручную проверку всех операций магазина.

## Отказ, восстановление и остановка

Останавливайте только свою базу, когда она не используется другими программами:

```powershell
docker compose -p panainte-pz12 stop db
# Проверьте отказ подключения и пустой каталог, затем:
docker compose -p panainte-pz12 start db
docker compose -p panainte-pz12 ps
docker compose -p panainte-pz12 run --rm db-check
```

Дождитесь `healthy`, перезапустите EXE и проверьте каталог. Программа сообщает
об ошибке соединения в консоли и оставляет пустой каталог, не удаляя данные.
Для обычной остановки инфраструктуры: `docker compose -p panainte-pz12 stop`.
Не используйте `down -v`, удаление тома или `volume prune`: именованный том
не заменяет отдельную резервную копию.

## Типичные проблемы

- Нет `config.ini`: создайте его рядом с EXE, используйте UTF-8 и секцию `[database]`.
- Нет БД: проверьте Docker, `compose ps`, порт, пароль и `db-check`; не печатайте `.env`.
- Ошибка Qt/DLL: восстановите всю папку onedir и запускайте из распакованной папки.
- Не хватает изображения: проверьте наличие `_internal/resources` и внешних
  пользовательских фотографий; пустое поле в БД означает заглушку, не ошибку сборки.
- При пересборке PyInstaller может собрать чужую ICU из PATH. Используйте
  `build_windows.ps1` из репозитория: он очищает PATH только для процесса сборки
  и затем восстанавливает окружение. Системные DLL заменять не нужно.

## Повторение сборки из Git

Из корня репозитория с установленным Python 3.10:

```powershell
py -3.10 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements-build.lock.txt
./.venv/Scripts/python.exe -m unittest discover -s tests -v
./build_windows.ps1
```

Spec содержит только `resources` и `app/ui` в `datas`; реальные настройки,
`.env`, резервные копии, виртуальное окружение и Git-метаданные в сборку не входят.
Консоль оставлена для диагностики. MSI, подпись, CI/CD-релиз и встроенный сервер
БД не создавались.
