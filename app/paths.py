"""Пути к поставляемым ресурсам и внешним пользовательским файлам."""
from pathlib import Path
import sys

BUNDLE_DIR = Path(__file__).resolve().parent.parent


def application_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return BUNDLE_DIR


def bundled_resource(relative_path):
    return BUNDLE_DIR / relative_path


def external_config_path():
    return application_dir() / "config.ini"


def user_images_dir():
    return application_dir() / "user-resources"


def product_image_path(filename):
    if filename:
        name = Path(filename).name
        for candidate in (user_images_dir() / name,
                          bundled_resource("resources") / name):
            if candidate.is_file():
                return candidate
    return bundled_resource("resources/picture.svg")
