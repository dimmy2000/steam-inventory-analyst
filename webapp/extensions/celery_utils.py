"""Функции для работы с Celery."""
from webapp.config import Config


def init_celery(celery, app):
    """Подключение экземпляра Celery к flask-приложению."""
    celery.config_from_object(Config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
