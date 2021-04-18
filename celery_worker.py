"""Настройка запуска воркера Celery."""
from webapp import celery
from webapp.extensions.celery_utils import init_celery
from webapp.factory import create_app

app = create_app()
init_celery(celery, app)
