import gevent
from gevent import monkey  # noqa: F401
gevent.monkey.patch_all()

from celery import Celery


def make_celery(app_name=__name__):
    """Cоздание экземпляра Celery."""
    return Celery(app_name)


celery = make_celery()
