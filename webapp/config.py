"""Здесь хранятся используемые в проекте переменные окружения."""
import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config(object):
    """Переменные для подключения к БД."""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..',
                                                          'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOG_TYPE = os.environ.get("LOG_TYPE") or "stream"
    LOG_LEVEL = os.environ.get("LOG_LEVEL") or "INFO"
    LOG_DIR = os.environ.get("LOG_DIR") or "./"
    APP_LOG_NAME = os.environ.get("APP_LOG_NAME") or "app.log"
    WWW_LOG_NAME = os.environ.get("WWW_LOG_NAME") or "www.log"
