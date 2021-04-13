"""Функции для работы с Celery."""


def init_celery(celery, app):
    """Подключение экземпляра Celery к flask-приложению."""
    celery.config_from_object('webapp.config')
    task_base = celery.Task

    class ContextTask(task_base):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return task_base.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
