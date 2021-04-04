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
