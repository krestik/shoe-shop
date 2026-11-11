import pandas as pd
import psycopg2
import os
from datetime import datetime
from app.db import DB_CONFIG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMPORT_DIR = os.path.join(BASE_DIR, 'import_files')


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def get_or_create(cursor, table, id_col, name_col, value):
    cursor.execute(f"SELECT {id_col} FROM {table} WHERE {name_col} = %s", (value,))
    res = cursor.fetchone()
    if res: return res[0]
    cursor.execute(f"INSERT INTO {table} ({name_col}) VALUES (%s) RETURNING {id_col}", (value,))
    return cursor.fetchone()[0]


def clean_date(date_val):
    if pd.isnull(date_val): return datetime.now()
    if isinstance(date_val, datetime): return date_val
    s = str(date_val).strip()
    if "30.02" in s or "29.02" in s: s = s.replace("30.02", "28.02").replace("29.02", "28.02")
    try:
        return datetime.strptime(s, "%d.%m.%Y")
    except:
        return datetime.now()


def import_data():
    conn = get_connection()
    cur = conn.cursor()
    print("Очистка...")
    cur.execute(
        "TRUNCATE OrderProduct, \"Order\", Product, ProductUnit, ProductSupplier, ProductManufacturer, ProductCategory, PickupPoint, \"User\" RESTART IDENTITY CASCADE;")

    # 1. Пункты
    print("Пункты...")
    df = pd.read_excel(os.path.join(IMPORT_DIR, 'Пункты_выдачи_import.xlsx'), header=None)
    for _, r in df.iterrows():
        cur.execute("INSERT INTO PickupPoint (point_address) VALUES (%s)", (str(r[0]).strip(),))

    # 2. Пользователи
    print("Пользователи...")
    df = pd.read_excel(os.path.join(IMPORT_DIR, 'user_import.xlsx'))
    for _, r in df.iterrows():
        role_id = get_or_create(cur, "Role", "role_id", "role_name", r['Роль сотрудника'])
        fio = r['ФИО'].split()
        s, n = fio[0], fio[1]
        p = fio[2] if len(fio) > 2 else ''
        cur.execute(
            "INSERT INTO \"User\" (user_surname, user_name, user_patronymic, user_login, user_password, user_role) VALUES (%s,%s,%s,%s,%s,%s)",
            (s, n, p, r['Логин'], r['Пароль'], role_id))

    # 3. Товары
    print("Товары...")
    df = pd.read_excel(os.path.join(IMPORT_DIR, 'Tovar.xlsx'))
    for _, r in df.iterrows():
        uid = get_or_create(cur, "ProductUnit", "unit_id", "unit_name", r['Единица измерения'])
        cid = get_or_create(cur, "ProductCategory", "category_id", "category_name", r['Категория товара'])
        mid = get_or_create(cur, "ProductManufacturer", "manufacturer_id", "manufacturer_name", r['Производитель'])
        sid = get_or_create(cur, "ProductSupplier", "supplier_id", "supplier_name", r['Поставщик'])

        cur.execute("""INSERT INTO Product (product_article, product_name, product_description, product_category, product_photo, 
                       product_manufacturer, product_supplier, product_cost, product_discount_amount, product_quantity_in_stock, product_unit)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (r['Артикул'], r['Наименование товара'], r['Описание товара'], cid, r['Фото'], mid, sid, r['Цена'],
                     r['Действующая скидка'], r['Кол-во на складе'], uid))

    # 4. Заказы
    print("Заказы...")
    df = pd.read_excel(os.path.join(IMPORT_DIR, 'Заказ_import.xlsx'))
    for _, r in df.iterrows():
        sid = get_or_create(cur, "OrderStatus", "status_id", "status_name", r['Статус заказа'])
        pid = int(r['Адрес пункта выдачи'])
        fio = r['ФИО авторизированного клиента'].split()
        cid = None
        if len(fio) >= 2:
            cur.execute("SELECT user_id FROM \"User\" WHERE user_surname=%s AND user_name=%s", (fio[0], fio[1]))
            res = cur.fetchone()
            if res: cid = res[0]

        cur.execute(
            "INSERT INTO \"Order\" (order_status, order_date, order_delivery_date, order_pickup_point, order_client_id, order_code) VALUES (%s,%s,%s,%s,%s,%s) RETURNING order_id",
            (sid, clean_date(r['Дата заказа']), clean_date(r['Дата доставки']), pid, cid, r['Код для получения']))
        oid = cur.fetchone()[0]

        items = str(r['Артикул заказа']).replace(" ", "").split(',')
        for i in range(0, len(items), 2):
            if i + 1 < len(items):
                # Проверка наличия товара
                cur.execute("SELECT 1 FROM Product WHERE product_article=%s", (items[i],))
                if cur.fetchone():
                    cur.execute(
                        "INSERT INTO OrderProduct (order_id, product_article, product_quantity) VALUES (%s,%s,%s)",
                        (oid, items[i], int(items[i + 1])))

    conn.commit()
    conn.close()
    print("=== ГОТОВО ===")


if __name__ == "__main__":
    import_data()