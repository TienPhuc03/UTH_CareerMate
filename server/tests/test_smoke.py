import importlib

from core.config import Settings


def test_settings_accept_release_debug():
    settings = Settings(
        DATABASE_URL="  mysql+pymysql://user:pass@localhost:3306/app  ",
        SECRET_KEY="secret",
        DEBUG="release",
    )

    assert settings.DEBUG is False
    assert settings.DATABASE_URL == "mysql+pymysql://user:pass@localhost:3306/app"


def test_main_module_imports():
    main = importlib.import_module("main")

    assert main.app.title == "CareerMate - AI Career Platform"
