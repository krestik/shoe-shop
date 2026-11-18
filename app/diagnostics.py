"""Автоматическая проверка реального приложения по явному --self-check."""
import argparse
import json
import os
from pathlib import Path
import platform
import sys

from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase

from app.db import get_db_connection
from app.paths import bundled_resource, external_config_path, product_image_path


def run_self_check(app, login_class, main_class, product_class):
    parser = argparse.ArgumentParser(description="Проверка ресурсов и чтения БД без изменения данных")
    parser.add_argument("--self-check", required=True, type=Path, metavar="OUTPUT_DIR")
    parser.add_argument("--expect-unavailable", action="store_true")
    args = parser.parse_args()
    out = args.self_check.resolve()
    out.mkdir(parents=True, exist_ok=True)
    font = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/times.ttf"
    if font.exists():
        QFontDatabase.addApplicationFont(str(font))
    checks = {}
    result = {"frozen": bool(getattr(sys, "frozen", False)),
              "executable": sys.executable, "cwd": str(Path.cwd()),
              "python": platform.python_version(), "qt_platform": app.platformName(),
              "render_mode": "Qt widgets hidden with WA_DontShowOnScreen",
              "config_path": str(external_config_path()), "checks": checks}
    windows = []
    try:
        # These are the same real UI classes used by normal interactive startup.
        login = login_class()
        login.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        login.show()
        app.processEvents()
        windows.append(login)
        checks["login_open"] = login.isVisible()
        checks["login_logo"] = login.label.pixmap() is not None and not login.label.pixmap().isNull()
        login.grab().save(str(out / "login.png"))
        window = main_class(None)
        window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        window.resize(1100, 650)
        window.show()
        app.processEvents()
        windows.append(window)
        checks["main_window_open"] = window.isVisible()
        checks["main_logo"] = window.label_logo_mini.pixmap() is not None and not window.label_logo_mini.pixmap().isNull()
        forms = ["login", "main_window", "product_edit", "order_edit", "orders_window"]
        for name in forms:
            form = uic.loadUi(str(bundled_resource("app/ui/" + name + ".ui")))
            form.close()
        checks["all_five_ui_files"] = True
        checks["fallback_image_exists"] = product_image_path(None).is_file()
        connection = get_db_connection()
        if connection is None:
            checks["expected_database_failure"] = args.expect_unavailable
            checks["empty_catalogue_without_crash"] = not window.all_products
            result["catalogue_count"] = len(window.all_products)
            result["database_available"] = False
        else:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT product_article, product_name, product_cost, product_quantity_in_stock, product_photo FROM Product ORDER BY product_article")
                    rows = cursor.fetchall()
                    cursor.execute("SELECT note FROM public.docker_persistence_check WHERE id=13")
                    marker = cursor.fetchone()
                    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'")
                    result["table_count"] = cursor.fetchone()[0]
            connection.close()
            actual = sorted((p[0], p[1], str(p[7]), int(p[9])) for p in window.all_products)
            expected = [(a, n, str(price), stock) for a, n, price, stock, photo in rows]
            cards = window.findChildren(product_class)
            checks["database_expected_available"] = not args.expect_unavailable
            checks["catalogue_matches_sql"] = actual == expected and bool(rows)
            checks["all_cards_have_images"] = len(cards) == len(rows) and all(c.image_label.pixmap() is not None and not c.image_label.pixmap().isNull() for c in cards)
            checks["marker_13_survived"] = marker == ("data survives recreation",)
            result.update({"database_available": True, "catalogue_count": len(rows),
                           "photo_count": sum(bool(r[4]) for r in rows),
                           "placeholder_count": sum(not bool(r[4]) for r in rows),
                           "products": [{"article": a, "name": n, "price": str(price), "stock": stock} for a, n, price, stock, photo in rows]})
        window.grab().save(str(out / "catalogue.png"))
        result["passed"] = all(checks.values())
    except Exception as error:
        result["passed"] = False
        # Exception type only: avoid exposing accidental configuration data.
        result["error_type"] = type(error).__name__
    finally:
        for window in windows:
            window.close()
        app.processEvents()
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0 if result["passed"] else 1
