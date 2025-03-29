# Standard library imports
import os

# Celery
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orders.settings")

app = Celery("backend")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.update(
    broker_url=os.getenv("REDIS_URL", "redis://redis:6379/0"),
)

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
