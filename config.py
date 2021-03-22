"""Здесь хранятся используемые в проекте переменные окружения."""
import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

# данные для подключения к PostgreSQL
DATABASE = os.getenv("DB_NAME")
LOGIN = os.getenv("POSTGRESQL_LOGIN")
PASSWORD = os.getenv("POSTGRESQL_PASSWORD")
PORT = os.getenv("POSTGRESQL_PORT")
URL = os.getenv("POSTGRESQL_URL")


class Config(object):
    """Переменные для подключения к БД."""

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = f'postgres://{LOGIN}:{PASSWORD}@{URL}:' \
    #                           f'{PORT}/{DATABASE}'
