"""Flask configuration."""
from pathlib import Path

# from dotenv import load_dotenv
from decouple import config

# basedir = path.abspath(path.dirname(__file__))
# # load_dotenv(path.join(basedir, '.env'))/

# Use this to build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


from api.conf.settings import settings

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


class Config:
    """class to hold application configuration."""
    SECRET_KEY = settings.SECRET_KEY
    DB_TYPE = settings.DB_TYPE
    # SESSION_COOKIE_NAME = settings.SESSION_COOKIE_NAME
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CKEDITOR_PKG_TYPE = "basic"
    STATIC_FOLDER: Path = BASE_DIR / "static"
    TEMPLATES_FOLDER: Path = BASE_DIR / "templates"

    SQLALCHEMY_DATABASE_URI = create_db_url(DB_TYPE)
    # f"postgresql://kufre:password@localhost/gofundme"
    #


class ProdConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False
    TESTING = False


class DevConfig(Config):
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = True
