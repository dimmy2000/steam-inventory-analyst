"""Здесь создается сессия подключения к серверу PostgreSQL."""
from .config import DB_NAME, POSTGRESQL_HOST, POSTGRESQL_LOGIN,\
    POSTGRESQL_PASSWORD, POSTGRESQL_PORT

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


engine = create_engine(f'postgres://{POSTGRESQL_LOGIN}:'
                       f'{POSTGRESQL_PASSWORD}@{POSTGRESQL_HOST}:'
                       f'{POSTGRESQL_PORT}/{DB_NAME}')
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
