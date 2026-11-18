import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app import db, paths


class PortableApplicationTests(unittest.TestCase):
    def test_frozen_config_uses_exe_folder_not_bundle(self):
        with tempfile.TemporaryDirectory() as folder:
            executable = Path(folder) / "portable" / "ShoeStore.exe"
            with patch.object(paths.sys, "frozen", True, create=True), patch.object(paths.sys, "executable", str(executable)):
                self.assertEqual(paths.external_config_path(), executable.parent / "config.ini")
                self.assertNotEqual(paths.external_config_path().parent, paths.BUNDLE_DIR)

    def test_source_config_does_not_depend_on_cwd(self):
        self.assertEqual(paths.external_config_path(), paths.BUNDLE_DIR / "config.ini")
        with patch("pathlib.Path.cwd", return_value=Path("C:/unrelated")):
            self.assertEqual(paths.bundled_resource("app/ui/login.ui"), paths.BUNDLE_DIR / "app/ui/login.ui")

    def test_missing_config_is_reported_without_exception(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(db, "external_config_path", return_value=Path(folder) / "missing.ini"):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertIsNone(db.read_db_config())
            self.assertIn("config.ini", output.getvalue())

    def test_percent_password_is_literal(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder) / "config.ini"
            config.write_text("[database]\nhost=127.0.0.1\nport=5433\nname=shoe_store\nuser=shoe_user\npassword=example%with%signs\n", encoding="utf-8")
            with patch.object(db, "external_config_path", return_value=config):
                result = db.read_db_config()
            self.assertEqual(result["password"], "example%with%signs")
            self.assertEqual(result["port"], 5433)

    def test_invalid_config_does_not_echo_password(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder) / "config.ini"
            config.write_text("[database]\nhost=127.0.0.1\nport=invalid\nname=shoe_store\nuser=shoe_user\npassword=example-private-value\n", encoding="utf-8")
            with patch.object(db, "external_config_path", return_value=config), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertIsNone(db.read_db_config())
            self.assertNotIn("example-private-value", output.getvalue())

    def test_uploaded_image_overrides_bundle_and_fallback_is_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "resources").mkdir()
            (base / "user-resources").mkdir()
            (base / "resources/photo.jpg").write_bytes(b"bundled")
            (base / "user-resources/photo.jpg").write_bytes(b"uploaded")
            with patch.object(paths, "BUNDLE_DIR", base), patch.object(paths, "application_dir", return_value=base):
                self.assertEqual(paths.product_image_path("photo.jpg"), base / "user-resources/photo.jpg")
                self.assertEqual(paths.product_image_path(None), base / "resources/picture.svg")


if __name__ == "__main__":
    unittest.main()
