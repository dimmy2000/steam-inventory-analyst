"""Здесь хранятся используемые в проекте переменные окружения."""
import os

from dotenv import load_dotenv

load_dotenv()

# данные для подключения к PostgreSQL
DB_NAME = os.getenv("DB_NAME")
POSTGRESQL_LOGIN = os.getenv("POSTGRESQL_LOGIN")
POSTGRESQL_PASSWORD = os.getenv("POSTGRESQL_PASSWORD")
POSTGRESQL_PORT = os.getenv("POSTGRESQL_PORT")
POSTGRESQL_HOST = os.getenv("POSTGRESQL_HOST")
