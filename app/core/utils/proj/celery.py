from celery import Celery
from core.conf.config import CeleryConfig


app = Celery()

app.config_from_object(CeleryConfig)

if __name__ == '__main__':
    app.start()