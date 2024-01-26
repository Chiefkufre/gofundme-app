from decouple import config


class Settings:
    DB_TYPE: str = config("DB_TYPE")
    DB_NAME: str = config("DB_NAME")
    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD", cast=str)
    DB_HOST: str = config("DB_HOST", cast=str)
    DB_PORT: int = config("DB_PORT", cast=int)
    MYSQL_DRIVER: str = config("MYSQL_DRIVER")
    SECRET_KEY: str = config("SECRET_KEY")
    JWT_SECRET_KEY = config("JWT_SECRET_KEY")
    SESSION_COOKIE_NAME: str = config("SESSION_COOKIE_NAME")

    MAIL_SERVER : str = config("MAIL_SERVER")
    MAIL_PORT : str = config("MAIL_PORT")
    MAIL_USERNAME : str = config("MAIL_USERNAME")
    MAIL_PASSWORD : str = config("MAIL_PASSWORD")
    MAIL_USE_TLS : bool = config("MAIL_USE_TLS")
    MAIL_USE_SSL : bool = config("MAIL_USE_SSL")

    API_VERSION: str = config("API_VERSION")


settings = Settings()
