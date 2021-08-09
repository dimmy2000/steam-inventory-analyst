"""Здесь хранятся используемые в проекте переменные окружения."""
import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config(object):
    """Хранение переменных для настройки компонентов приложения."""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dQw4w9WgXcQ"
    # SQL database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..',
                                                          'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Logging
    LOG_TYPE = os.environ.get("LOG_TYPE") or "stream"
    LOG_LEVEL = os.environ.get("LOG_LEVEL") or "INFO"
    LOG_DIR = os.environ.get("LOG_DIR") or "./"
    APP_LOG_NAME = os.environ.get("APP_LOG_NAME") or "app.log"
    WWW_LOG_NAME = os.environ.get("WWW_LOG_NAME") or "www.log"
    # Celery configuration
    worker_hijack_root_logger = False
    accept_content = ["msgpack", "json"]
    broker_url = "redis://localhost:6379/0"
    result_backend = "redis://localhost:6379/1"
    task_serializer = "msgpack"
