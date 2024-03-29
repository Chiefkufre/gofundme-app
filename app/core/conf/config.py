"""Flask configuration."""
from pathlib import Path

import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta

# from dotenv import load_dotenv
from decouple import config

# basedir = path.abspath(path.dirname(__file__))
# # load_dotenv(path.join(basedir, '.env'))/

# Use this to build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


from core.conf.settings import settings

DB_TYPE = settings.DB_TYPE
DB_NAME = settings.DB_NAME
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
MYSQL_DRIVER = settings.MYSQL_DRIVER


def create_db_url(DB_TYPE):
    if DB_TYPE == "postgresql":
        DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    # :{DB_PORT}/
    if DB_TYPE == "mysql":
        DATABASE_URI = f"mysql+{MYSQL_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    elif DB_TYPE == "sqlite":
        DATABASE_URI = "sqlite:///database.db"

    return DATABASE_URI


def set_result_backend(db_type):
    result_backend = ""
    if db_type == "postgres":
        result_backend = (
            "db+postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    elif db_type == "mysql":
        result_backend = (
            "db+mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    else:
        result_backend = "sqlite:///celery_results.db"

    return result_backend


class Logger:
    LOG_LEVEL = logging.DEBUG

    @staticmethod
    def init_app(app):
        app.logger.setLevel(Logger.LOG_LEVEL)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(Logger.LOG_LEVEL)
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)

        file_handler = RotatingFileHandler("app.log", maxBytes=10240, backupCount=5)
        file_handler.setLevel(Logger.LOG_LEVEL)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)


class MailConfig:
    MAIL_SERVER = settings.MAIL_SERVER
    MAIL_PORT = settings.MAIL_PORT
    MAIL_USERNAME = settings.MAIL_USERNAME
    MAIL_PASSWORD = settings.MAIL_PASSWORD
    MAIL_USE_TLS = settings.MAIL_USE_TLS
    MAIL_USE_SSL = settings.MAIL_USE_SSL


class Config(MailConfig):
    """class to hold application configuration."""

    SECRET_KEY = settings.SECRET_KEY
    DB_TYPE = settings.DB_TYPE
    # SESSION_COOKIE_NAME = settings.SESSION_COOKIE_NAME
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER: Path = BASE_DIR / "static"
    TEMPLATES_FOLDER: Path = BASE_DIR / "templates"

    SQLALCHEMY_DATABASE_URI = create_db_url(DB_TYPE)
    # f"postgresql://kufre:password@localhost/gofundme"
    #
    JWT_SECRET_KEY = settings.JWT_SECRET_KEY
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)


class ProdConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False
    TESTING = False


class DevConfig(Config):
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = True


class CeleryConfig:
    broker_url = ("redis://localhost:6379/",)
    result_backend = (set_result_backend(DB_TYPE),)
    include = ["proj.tasks"]
    result_expires = 3600
