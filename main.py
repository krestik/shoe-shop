import os
import random
import shutil
import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtWidgets import QMessageBox, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, QFrame
from app.db import get_db_connection


class ProductWidget(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, product_data, is_admin):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.data = product_data
        self.is_admin = is_admin

        self.article = product_data[0]
        self.name = product_data[1]
        self.desc = product_data[2]
        self.cat = product_data[3]
        self.photo = product_data[4]
        self.manuf = product_data[5]
        self.supplier = product_data[6]
        self.cost = float(product_data[7])
        self.discount = int(product_data[8])
        self.quantity = int(product_data[9])
        self.unit = product_data[10]

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        if self.is_admin:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.image_label = QLabel()
        self.image_label.setFixedSize(120, 100)
        self.image_label.setScaledContents(True)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        img_path = None
        if self.photo:
            possible = os.path.join(os.path.dirname(__file__), 'resources', self.photo)
            if os.path.exists(possible):
                img_path = possible
            elif os.path.exists(self.photo):
                img_path = self.photo
        if not img_path:
            img_path = os.path.join(os.path.dirname(__file__), 'resources', 'picture.png')

        if os.path.exists(img_path):
            self.image_label.setPixmap(QPixmap(img_path))
        else:
            self.image_label.setText("Фото")
        main_layout.addWidget(self.image_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        line1 = QLabel(f"<b>{self.cat} | {self.name}</b>")
        line1.setStyleSheet("border: none; background: transparent;")
        info_layout.addWidget(line1)

        desc_text = self.desc if self.desc else ""
        line2 = QLabel(f"Описание товара: {desc_text}")
        line2.setWordWrap(True)
        line2.setStyleSheet("border: none; background: transparent;")
        info_layout.addWidget(line2)

        line3 = QLabel(f"Производитель: {self.manuf}")
        line3.setStyleSheet("border: none; background: transparent;")
        info_layout.addWidget(line3)

        line4 = QLabel(f"Поставщик: {self.supplier}")
        line4.setStyleSheet("border: none; background: transparent;")
        info_layout.addWidget(line4)

        final_price = self.cost
        price_text = ""
        if self.discount > 0:
            final_price = self.cost * (1 - self.discount / 100)
            price_text = f"Цена: <s><span style='color:red'>{self.cost:.2f}</span></s> <span style='color:black'>{final_price:.2f} руб.</span>"
        else:
            price_text = f"Цена: {self.cost:.2f} руб."
        price_label = QLabel(price_text)
        price_label.setStyleSheet("border: none; background: transparent;")
        info_layout.addWidget(price_label)

        line6 = QLabel(f"Единица измерения: {self.unit}")
        line6.setStyleSheet("border: none; background: transparent;")
        info_layout.addWidget(line6)

        line7 = QLabel(f"Количество на складе: {'много' if self.quantity > 5 else 'мало'} ({self.quantity})")
        if self.quantity <= 0:
            line7.setStyleSheet("background-color: #87CEEB; border: none;")
        else:
            line7.setStyleSheet("border: none; background: transparent;")
        info_layout.addWidget(line7)

        info_layout.addStretch()
        main_layout.addLayout(info_layout, stretch=1)

        discount_text = f"Действующая\nскидка\n{self.discount}%" if self.discount > 0 else "Действующая\nскидка\n0%"
        disc_label = QLabel(discount_text)
        disc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        disc_label.setFixedWidth(100)
        disc_label.setStyleSheet("border-left: 1px solid black; background: transparent;")
        main_layout.addWidget(disc_label)

        bg_color = "#FFFFFF"
        if self.discount > 15: bg_color = "#2E8B57"
        self.setStyleSheet(f"ProductWidget {{ background-color: {bg_color}; border: 1px solid black; }}")

    def mousePressEvent(self, event):
        if self.is_admin: self.clicked.emit(self.article)
        super().mousePressEvent(event)


class OrderWidget(QWidget):
    clicked = pyqtSignal(int)

    def __init__(self, order_data, is_admin):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.id = order_data[0]
        self.is_admin = is_admin

        layout = QHBoxLayout()
        self.setLayout(layout)
        if self.is_admin: self.setCursor(Qt.CursorShape.PointingHandCursor)

        left = QVBoxLayout()
        lbl_id = QLabel(f"Заказ № {self.id}")
        lbl_id.setFont(QFont("Times New Roman", 12, QFont.Weight.Bold))
        lbl_id.setStyleSheet("border: none; background: transparent;")
        lbl_stat = QLabel(f"Статус: {order_data[1]}")
        lbl_stat.setStyleSheet("border: none; background: transparent;")
        lbl_addr = QLabel(f"Пункт выдачи: {order_data[4]}")
        lbl_addr.setWordWrap(True)
        lbl_addr.setStyleSheet("border: none; background: transparent;")
        date_str = order_data[2].strftime("%d.%m.%Y") if order_data[2] else ""
        lbl_date = QLabel(f"Дата заказа: {date_str}")
        lbl_date.setStyleSheet("border: none; background: transparent;")

        left.addWidget(lbl_id);
        left.addWidget(lbl_stat);
        left.addWidget(lbl_addr);
        left.addWidget(lbl_date)
        layout.addLayout(left, stretch=1)

        right = QVBoxLayout()
        del_str = order_data[3].strftime("%d.%m.%Y") if order_data[3] else ""
        lbl_del = QLabel(f"Дата доставки:\n{del_str}")
        lbl_del.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        lbl_del.setStyleSheet("border: none; background: transparent;")
        right.addWidget(lbl_del);
        right.addStretch()
        layout.addLayout(right)

        self.setStyleSheet("OrderWidget { border: 2px solid #00FA9A; border-radius: 5px; background-color: white; }")

    def mousePressEvent(self, e):
        if self.is_admin: self.clicked.emit(self.id)
        super().mousePressEvent(e)


class ProductEditWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, article=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'app', 'ui', 'product_edit.ui'), self)
        self.article = article
        self.parent_window = parent
        self.current_image_path = None

        self.cats = [];
        self.manufs = [];
        self.supps = [];
        self.units = []

        self.btn_save.clicked.connect(self.save)
        self.btn_delete.clicked.connect(self.delete)
        self.btn_back.clicked.connect(self.close)
        self.btn_change_image.clicked.connect(self.choose_image)

        self.load_combos()
        if self.article:
            self.load_data()
            self.line_article.setReadOnly(True)
        else:
            self.btn_save.setText("Добавить")
            self.btn_delete.setVisible(False)

    def load_combos(self):
        conn = get_db_connection()
        if not conn: return
        cur = conn.cursor()

        cur.execute("SELECT * FROM ProductCategory")
        for r in cur.fetchall(): self.cats.append(r[0]); self.combo_category.addItem(r[1])

        cur.execute("SELECT * FROM ProductManufacturer")
        for r in cur.fetchall(): self.manufs.append(r[0]); self.combo_manufacturer.addItem(r[1])

        cur.execute("SELECT * FROM ProductSupplier")
        for r in cur.fetchall(): self.supps.append(r[0]); self.combo_supplier.addItem(r[1])

        cur.execute("SELECT * FROM ProductUnit")
        for r in cur.fetchall(): self.units.append(r[0]); self.combo_unit.addItem(r[1])
        conn.close()

    def load_data(self):
        conn = get_db_connection();
        cur = conn.cursor()
        cur.execute("SELECT * FROM Product WHERE product_article=%s", (self.article,))
        row = cur.fetchone()
        conn.close()
        if row:
            self.line_article.setText(self.article)
            self.line_name.setText(row[1])
            self.text_description.setText(row[2])

            try:
                self.combo_category.setCurrentIndex(self.cats.index(row[3]))
            except:
                pass

            self.current_image_path = row[4]

            try:
                self.combo_manufacturer.setCurrentIndex(self.manufs.index(row[5]))
            except:
                pass
            try:
                self.combo_supplier.setCurrentIndex(self.supps.index(row[6]))
            except:
                pass

            self.spin_cost.setValue(float(row[7]))
            self.spin_discount.setValue(int(row[8]))
            self.spin_quantity.setValue(int(row[9]))

            try:
                self.combo_unit.setCurrentIndex(self.units.index(row[10]))
            except:
                pass

            self.update_image()

    def update_image(self):
        p = None
        if self.current_image_path:
            t = os.path.join(os.path.dirname(__file__), 'resources', self.current_image_path)
            if os.path.exists(t): p = t
        if not p: p = os.path.join(os.path.dirname(__file__), 'resources', 'picture.png')
        self.label_image.setPixmap(QPixmap(p).scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio))

    def choose_image(self):
        try:
            fp, _ = QFileDialog.getOpenFileName(self, "Выбрать", "", "Images (*.png *.jpg)")
            if fp:
                fn = os.path.basename(fp)
                dest_dir = os.path.join(os.path.dirname(__file__), 'resources')

                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)

                dest = os.path.join(dest_dir, fn)

                if os.path.abspath(fp) != os.path.abspath(dest):
                    shutil.copy(fp, dest)

                self.current_image_path = fn
                self.update_image()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка фото", str(e))

    def save(self):
        art = self.line_article.text().strip()
        name = self.line_name.text().strip()
        if not art or not name: return QMessageBox.warning(self, "!", "Заполните поля")

        cid = self.cats[self.combo_category.currentIndex()]
        mid = self.manufs[self.combo_manufacturer.currentIndex()]
        sid = self.supps[self.combo_supplier.currentIndex()]
        uid = self.units[self.combo_unit.currentIndex()]

        args = (name, self.text_description.toPlainText(), cid, self.current_image_path,
                mid, sid, self.spin_cost.value(), self.spin_discount.value(),
                self.spin_quantity.value(), uid)

        conn = get_db_connection();
        cur = conn.cursor()
        try:
            if self.article:
                cur.execute("""UPDATE Product SET product_name=%s, product_description=%s, product_category=%s,
                               product_photo=%s, product_manufacturer=%s, product_supplier=%s, product_cost=%s,
                               product_discount_amount=%s, product_quantity_in_stock=%s, product_unit=%s
                               WHERE product_article=%s""", (*args, self.article))
            else:
                cur.execute("SELECT 1 FROM Product WHERE product_article=%s", (art,))
                if cur.fetchone(): return QMessageBox.warning(self, "!", "Артикул занят")
                cur.execute("""INSERT INTO Product VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (art, *args))
            conn.commit()
            self.parent_window.load_data()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Err", str(e))
        finally:
            conn.close()

    def delete(self):
        if QMessageBox.question(self, "?", "Удалить?") == QMessageBox.StandardButton.Yes:
            conn = get_db_connection();
            cur = conn.cursor()
            try:
                cur.execute("SELECT 1 FROM OrderProduct WHERE product_article=%s", (self.article,))
                if cur.fetchone(): return QMessageBox.warning(self, "Err", "Товар в заказе")
                cur.execute("DELETE FROM Product WHERE product_article=%s", (self.article,))
                conn.commit()
                self.parent_window.load_data()
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Err", str(e))
            finally:
                conn.close()


class OrderEditWindow(QtWidgets.QMainWindow):
    def __init__(self, parent_controller, order_id=None):
        super().__init__(None)
        self.parent_controller = parent_controller
        self.order_id = order_id
        self.order_items = []

        try:
            uic.loadUi(os.path.join(os.path.dirname(__file__), 'app', 'ui', 'order_edit.ui'), self)

            self.stats = []
            self.points = []
            self.clients = []
            self.products = []
            self.load_refs()

            if order_id:
                self.label_id.setText(f"Заказ № {order_id}")
                self.load_data()
            else:
                self.label_id.setText("Новый заказ")
                self.btn_delete.setVisible(False)
                self.date_delivery.setDate(QDate.currentDate().addDays(3))

            self.btn_save.clicked.connect(self.save)
            self.btn_delete.clicked.connect(self.delete)
            self.btn_add_item.clicked.connect(self.add_item)
            self.btn_del_item.clicked.connect(self.del_item)

        except Exception as e:
            QMessageBox.critical(None, "Err", str(e))
            self.close()

    def load_refs(self):
        conn = get_db_connection();
        cur = conn.cursor()
        cur.execute("SELECT * FROM OrderStatus")
        for r in cur.fetchall(): self.stats.append(r[0]); self.combo_status.addItem(r[1])

        cur.execute("SELECT * FROM PickupPoint")
        for r in cur.fetchall(): self.points.append(r[0]); self.combo_point.addItem(r[1])

        cur.execute("SELECT user_id, user_surname, user_name, user_patronymic FROM \"User\"")
        for r in cur.fetchall():
            fio = f"{r[1]} {r[2]} {r[3]}".strip()
            self.clients.append(r[0]);
            self.combo_client.addItem(fio)

        cur.execute("SELECT product_article, product_name FROM Product")
        for r in cur.fetchall():
            self.products.append(r)
            self.combo_product.addItem(f"{r[1]} ({r[0]})")

        conn.close()

    def load_data(self):
        conn = get_db_connection();
        cur = conn.cursor()

        cur.execute(
            "SELECT order_status, order_delivery_date, order_pickup_point, order_client_id FROM \"Order\" WHERE order_id=%s",
            (self.order_id,))
        row = cur.fetchone()

        if row:
            try:
                self.combo_status.setCurrentIndex(self.stats.index(row[0]))
            except:
                pass
            try:
                d = row[1]; self.date_delivery.setDate(QDate(d.year, d.month, d.day))
            except:
                pass
            try:
                self.combo_point.setCurrentIndex(self.points.index(row[2]))
            except:
                pass
            try:
                self.combo_client.setCurrentIndex(self.clients.index(row[3]))
            except:
                pass

        cur.execute("""
            SELECT p.product_article, p.product_name, op.product_quantity 
            FROM OrderProduct op
            JOIN Product p ON op.product_article = p.product_article
            WHERE op.order_id = %s
        """, (self.order_id,))

        for r in cur.fetchall():
            self.order_items.append({'article': r[0], 'name': r[1], 'qty': r[2]})

        self.update_items_list()
        conn.close()

    def update_items_list(self):
        self.list_products.clear()
        for item in self.order_items:
            self.list_products.addItem(f"{item['article']} | {item['name']} — {item['qty']} шт.")

    def add_item(self):
        idx = self.combo_product.currentIndex()
        if idx < 0: return

        prod = self.products[idx]
        qty = self.spin_qty.value()

        for item in self.order_items:
            if item['article'] == prod[0]:
                item['qty'] += qty
                self.update_items_list()
                return

        self.order_items.append({'article': prod[0], 'name': prod[1], 'qty': qty})
        self.update_items_list()

    def del_item(self):
        row = self.list_products.currentRow()
        if row >= 0:
            self.order_items.pop(row)
            self.update_items_list()

    def save(self):
        if not self.stats or not self.points: return

        idx = self.combo_status.currentIndex()
        if idx < 0 or idx >= len(self.stats): return

        stat_id = self.stats[idx]
        point_id = self.points[self.combo_point.currentIndex()]
        d_date = self.date_delivery.date().toString("yyyy-MM-dd")

        idx_c = self.combo_client.currentIndex()
        cid = self.clients[idx_c] if (self.clients and idx_c >= 0) else None

        conn = get_db_connection();
        cur = conn.cursor()
        try:
            if self.order_id:
                cur.execute(
                    "UPDATE \"Order\" SET order_status=%s, order_delivery_date=%s, order_pickup_point=%s, order_client_id=%s WHERE order_id=%s",
                    (stat_id, d_date, point_id, cid, self.order_id))
            else:
                code = random.randint(100, 999)
                cur.execute(
                    "INSERT INTO \"Order\" (order_status, order_date, order_delivery_date, order_pickup_point, order_client_id, order_code) VALUES (%s, CURRENT_DATE, %s, %s, %s, %s) RETURNING order_id",
                    (stat_id, d_date, point_id, cid, code))
                self.order_id = cur.fetchone()[0]

            cur.execute("DELETE FROM OrderProduct WHERE order_id=%s", (self.order_id,))
            for item in self.order_items:
                cur.execute(
                    "INSERT INTO OrderProduct (order_id, product_article, product_quantity) VALUES (%s, %s, %s)",
                    (self.order_id, item['article'], item['qty']))

            conn.commit()
            QMessageBox.information(self, "OK", "Заказ сохранен")
            self.parent_controller.load_orders()
            self.close()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Err", str(e))
        finally:
            conn.close()

    def delete(self):
        if QMessageBox.question(self, "?", "Удалить?") == QMessageBox.StandardButton.Yes:
            conn = get_db_connection();
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM OrderProduct WHERE order_id=%s", (self.order_id,))
                cur.execute("DELETE FROM \"Order\" WHERE order_id=%s", (self.order_id,))
                conn.commit()
                self.parent_controller.load_orders()
                self.close()
            except Exception as e:
                conn.rollback()
                QMessageBox.critical(self, "Err", str(e))
            finally:
                conn.close()


class OrdersWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, is_admin=False):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'app', 'ui', 'orders_window.ui'), self)
        self.is_admin = is_admin
        self.btn_back.clicked.connect(self.close)
        if self.is_admin:
            self.btn_add.clicked.connect(self.add_order)
        else:
            self.btn_add.setVisible(False)
        self.load_orders()

    def load_orders(self):
        while self.verticalLayout_list.count():
            item = self.verticalLayout_list.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        conn = get_db_connection();
        cur = conn.cursor()
        cur.execute("""
            SELECT o.order_id, s.status_name, o.order_date, o.order_delivery_date, 
                   p.point_address, u.user_surname
            FROM "Order" o
            JOIN OrderStatus s ON o.order_status = s.status_id
            JOIN PickupPoint p ON o.order_pickup_point = p.point_id
            LEFT JOIN "User" u ON o.order_client_id = u.user_id
            ORDER BY o.order_date DESC
        """)
        for r in cur.fetchall():
            wid = OrderWidget(r, self.is_admin)
            wid.clicked.connect(self.open_edit)
            self.verticalLayout_list.addWidget(wid)
        self.verticalLayout_list.addStretch()

    def open_edit(self, order_id):
        if not self.is_admin: return
        self.win = OrderEditWindow(self, order_id)
        self.win.show()

    def add_order(self):
        self.win = OrderEditWindow(self, None)
        self.win.show()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, user_data=None):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'app', 'ui', 'main_window.ui'), self)
        self.user_data = user_data

        role = self.user_data[6] if self.user_data else 0
        self.is_admin = (role == 1)
        self.is_manager = (role == 2)

        self.btn_add_product.setVisible(self.is_admin)
        self.btn_add_product.setEnabled(self.is_admin)
        self.btn_orders.setVisible(self.is_admin or self.is_manager)

        if not self.is_admin and not self.is_manager: self.filterGroup.setVisible(False)

        fio = "Гость"
        if self.user_data: fio = f"{self.user_data[1]} {self.user_data[2]} {self.user_data[3]}".strip()
        self.label_fio.setText(fio)

        self.btn_exit.clicked.connect(self.logout)
        self.btn_add_product.clicked.connect(self.open_add_product)
        self.btn_orders.clicked.connect(self.open_orders)

        self.combo_sort.currentIndexChanged.connect(self.update_list)
        self.combo_filter.currentIndexChanged.connect(self.update_list)
        self.lineEdit_search.textChanged.connect(self.update_list)

        self.load_suppliers()
        self.load_data()

    def load_suppliers(self):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT supplier_name FROM ProductSupplier")
            for s in cursor.fetchall(): self.combo_filter.addItem(s[0])
            conn.close()

    def load_data(self):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = """
                SELECT p.product_article, p.product_name, p.product_description, c.category_name, 
                       p.product_photo, m.manufacturer_name, s.supplier_name, p.product_cost, 
                       p.product_discount_amount, p.product_quantity_in_stock, u.unit_name
                FROM Product p
                JOIN ProductCategory c ON p.product_category = c.category_id
                JOIN ProductManufacturer m ON p.product_manufacturer = m.manufacturer_id
                JOIN ProductSupplier s ON p.product_supplier = s.supplier_id
                JOIN ProductUnit u ON p.product_unit = u.unit_id
            """
            cursor.execute(query)
            self.all_products = cursor.fetchall()
            conn.close()
            self.update_list()

    def update_list(self):
        layout = self.verticalLayout_list
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        search = self.lineEdit_search.text().lower()
        filt = self.combo_filter.currentText()
        sort = self.combo_sort.currentIndex()

        filtered = []
        for p in self.all_products:
            name_check = search not in p[1].lower()
            desc_check = search not in (p[2] or "").lower()
            if search and (name_check and desc_check): continue
            if filt != "Все поставщики" and p[6] != filt: continue
            filtered.append(p)

        if sort == 1:
            filtered.sort(key=lambda x: x[9])
        elif sort == 2:
            filtered.sort(key=lambda x: x[9], reverse=True)

        for prod in filtered:
            wid = ProductWidget(prod, self.is_admin)
            wid.clicked.connect(self.open_edit_product)
            layout.addWidget(wid)
        layout.addStretch()
        self.label_count.setText(f"Показано {len(filtered)} из {len(self.all_products)}")

    def open_add_product(self):
        self.win = ProductEditWindow(self, None)
        self.win.show()

    def open_edit_product(self, article):
        self.win = ProductEditWindow(self, article)
        self.win.show()

    def open_orders(self):
        self.win = OrdersWindow(self, self.is_admin)
        self.win.show()

    def logout(self):
        self.login = LoginWindow()
        self.login.show()
        self.close()


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'app', 'ui', 'login.ui'), self)
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_guest.clicked.connect(self.handle_guest)

    def handle_login(self):
        l, p = self.lineEdit_login.text().strip(), self.lineEdit_password.text().strip()
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM "User" WHERE user_login=%s AND user_password=%s', (l, p))
            user = cur.fetchone()
            conn.close()
            if user:
                self.open_main(user)
            else:
                QMessageBox.warning(self, "!", "Неверный логин или пароль. Проверьте введённые данные")

    def handle_guest(self):
        self.open_main(None)

    def open_main(self, user):
        self.main = MainWindow(user)
        self.main.show()
        self.close()


if __name__ == '__main__':
    if hasattr(QtWidgets.QApplication, 'setHighDpiScaleFactorRoundingPolicy'):
        QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    app.setStyleSheet("""
        QWidget { color: #000000; font-family: 'Times New Roman'; font-size: 14px; }
        QMainWindow { background-color: #FFFFFF; }
        QLineEdit, QComboBox, QSpinBox, QDateEdit, QDoubleSpinBox, QTextEdit, QListWidget { 
            background-color: white; border: 1px solid #CCCCCC; padding: 2px; color: black;
        }
        QPushButton {
            background-color: #00FA9A;
            border: 1px solid #00AA66;
            border-radius: 4px;
            padding: 5px;
            color: black;
        }
        QPushButton:hover { background-color: #00FFBB; }
        QPushButton:disabled { background-color: #CCCCCC; }
    """)

    icon = os.path.join(os.path.dirname(__file__), 'resources', 'icon.ico')
    if os.path.exists(icon): app.setWindowIcon(QIcon(icon))

    w = LoginWindow()
    w.show()
    sys.exit(app.exec())