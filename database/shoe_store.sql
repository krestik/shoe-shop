-- shoe_store.sql — скрипт базы данных «Магазин обуви» со справочными данными.
-- Создание базы: CREATE DATABASE shoe_store;
-- Загрузка: psql -U shoe_user -d shoe_store -f database/shoe_store.sql

DROP TABLE IF EXISTS OrderProduct CASCADE;
DROP TABLE IF EXISTS "Order" CASCADE;
DROP TABLE IF EXISTS OrderStatus CASCADE;
DROP TABLE IF EXISTS PickupPoint CASCADE;
DROP TABLE IF EXISTS Product CASCADE;
DROP TABLE IF EXISTS ProductUnit CASCADE;
DROP TABLE IF EXISTS ProductSupplier CASCADE;
DROP TABLE IF EXISTS ProductManufacturer CASCADE;
DROP TABLE IF EXISTS ProductCategory CASCADE;
DROP TABLE IF EXISTS "User" CASCADE;
DROP TABLE IF EXISTS Role CASCADE;

CREATE TABLE Role (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(100) NOT NULL
);

CREATE TABLE "User" (
    user_id SERIAL PRIMARY KEY,
    user_surname VARCHAR(100) NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    user_patronymic VARCHAR(100) NOT NULL,
    user_login VARCHAR(100) NOT NULL UNIQUE,
    user_password VARCHAR(100) NOT NULL,
    user_role INT NOT NULL REFERENCES Role(role_id)
);

CREATE TABLE ProductCategory (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

CREATE TABLE ProductManufacturer (
    manufacturer_id SERIAL PRIMARY KEY,
    manufacturer_name VARCHAR(100) NOT NULL
);

CREATE TABLE ProductSupplier (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL
);

CREATE TABLE ProductUnit (
    unit_id SERIAL PRIMARY KEY,
    unit_name VARCHAR(50) NOT NULL
);

CREATE TABLE Product (
    product_article VARCHAR(100) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    product_description TEXT,
    product_category INT NOT NULL REFERENCES ProductCategory(category_id),
    product_photo VARCHAR(255),
    product_manufacturer INT NOT NULL REFERENCES ProductManufacturer(manufacturer_id),
    product_supplier INT NOT NULL REFERENCES ProductSupplier(supplier_id),
    product_cost DECIMAL(19, 4) NOT NULL,
    product_discount_amount INT DEFAULT 0,
    product_quantity_in_stock INT NOT NULL,
    product_unit INT NOT NULL REFERENCES ProductUnit(unit_id)
);

CREATE TABLE OrderStatus (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(100) NOT NULL
);

CREATE TABLE PickupPoint (
    point_id SERIAL PRIMARY KEY,
    point_address VARCHAR(255) NOT NULL
);

CREATE TABLE "Order" (
    order_id SERIAL PRIMARY KEY,
    order_status INT NOT NULL REFERENCES OrderStatus(status_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    order_delivery_date TIMESTAMP NOT NULL,
    order_pickup_point INT NOT NULL REFERENCES PickupPoint(point_id),
    order_client_id INT REFERENCES "User"(user_id),
    order_code INT NOT NULL
);

CREATE TABLE OrderProduct (
    order_id INT NOT NULL REFERENCES "Order"(order_id),
    product_article VARCHAR(100) NOT NULL REFERENCES Product(product_article),
    product_quantity INT NOT NULL,
    PRIMARY KEY (order_id, product_article)
);

INSERT INTO Role (role_name) VALUES
('Администратор'),
('Менеджер'),
('Клиент');

INSERT INTO "User" (user_surname, user_name, user_patronymic, user_login, user_password, user_role) VALUES
('Админов', 'Админ', 'Админович', 'admin', '12345', 1),
('Менеджеров', 'Петр', 'Петрович', 'manager', '12345', 2),
('Клиентов', 'Иван', 'Иванович', 'client', '12345', 3);

INSERT INTO ProductCategory (category_name) VALUES ('Ботинки'), ('Кроссовки'), ('Туфли');
INSERT INTO ProductManufacturer (manufacturer_name) VALUES ('Nike'), ('Adidas'), ('Puma');
INSERT INTO ProductSupplier (supplier_name) VALUES ('OOO Sport'), ('Mir Obuvi');
INSERT INTO ProductUnit (unit_name) VALUES ('шт.'), ('пара');

INSERT INTO Product (product_article, product_name, product_description, product_category, product_photo, product_manufacturer, product_supplier, product_cost, product_discount_amount, product_quantity_in_stock, product_unit)
VALUES ('A100', 'Ботинки Зимние', 'Теплые, удобные', 1, '1.jpg', 1, 1, 5000.00, 5, 10, 2);

INSERT INTO Product (product_article, product_name, product_description, product_category, product_photo, product_manufacturer, product_supplier, product_cost, product_discount_amount, product_quantity_in_stock, product_unit)
VALUES ('B200', 'Кроссовки Летние', 'Легкие для бега', 2, '', 2, 2, 3000.00, 20, 50, 2);

INSERT INTO Product (product_article, product_name, product_description, product_category, product_photo, product_manufacturer, product_supplier, product_cost, product_discount_amount, product_quantity_in_stock, product_unit)
VALUES ('C300', 'Туфли Классика', 'На выход', 3, '', 3, 1, 7000.00, 0, 0, 2);

INSERT INTO OrderStatus (status_name) VALUES ('Новый'), ('В обработке'), ('Завершен'), ('Отменен');
INSERT INTO PickupPoint (point_address) VALUES ('ул. Ленина, 1'), ('пр. Мира, 15');

INSERT INTO "Order" (order_status, order_date, order_delivery_date, order_pickup_point, order_client_id, order_code)
VALUES (1, '2025-02-28 10:00:00', '2025-03-05 10:00:00', 1, 3, 123);

INSERT INTO "Order" (order_status, order_date, order_delivery_date, order_pickup_point, order_client_id, order_code)
VALUES (3, '2025-01-15 12:00:00', '2025-01-20 12:00:00', 2, 3, 456);

INSERT INTO OrderProduct (order_id, product_article, product_quantity) VALUES (1, 'A100', 1);
INSERT INTO OrderProduct (order_id, product_article, product_quantity) VALUES (1, 'B200', 2);
INSERT INTO OrderProduct (order_id, product_article, product_quantity) VALUES (2, 'C300', 1);
