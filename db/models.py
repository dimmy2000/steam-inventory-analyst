"""Здесь покоятся модели баз данных."""
from db import Base, engine

from sqlalchemy import Column, Integer, String


class User(Base):
    """Модель таблицы авторизованных пользователей."""

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    steam_id = Column(String(17), unique=True)
    user_login = Column(String)
    avatar_url = Column(String)
    wallet_balance = Column(Integer)
    currency = Column(String(3))

    def __repr__(self):
        """Определяем формат вывода объекта класса User."""
        return f"User {self.user_id}, {self.user_login}, {self.steam_id}"


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
