from decouple import config

class Settings:
    DB_TYPE : str = config("DB_TYPE")
    DB_NAME: str = config("DB_NAME")
    DB_USER: str= config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")
    DB_HOST: str = ("DB_HOST")
    DB_PORT: int = config("DB_PORT", cast=int)
    MYSQL_DRIVER: str = config("MYSQL_DRIVER")
    SECRET_KEY: str = config("SECRET_KEY")
    SESSION_COOKIE_NAME:str  = config("SESSION_COOKIE_NAME")




settings = Settings()