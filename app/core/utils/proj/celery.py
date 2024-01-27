from celery import Celery

celery = Celery(
    "proj",
    broker_url="redis://localhost:6379/",
    result_backend="redis://localhost",
    include=["core.utils.proj.tasks"],
    result_expires=3600,
)


if __name__ == "__main__":
    celery.start()
