"""Здесь покоятся модели баз данных."""
from db import Base, engine

from sqlalchemy import BigInteger, Column, Integer, String


class User(Base):
    """Модель таблицы авторизованных пользователей."""

    __tablename__ = "users"

    steam_id = Column(BigInteger, unique=True, primary_key=True)
    user_login = Column(String, unique=True, nullable=False)
    avatar_url = Column(String, nullable=False)
    wallet_balance = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False)

    def __repr__(self):
        """Определяем формат вывода объекта класса User."""
        bucks, cents = divmod(self.wallet_balance, 100)
        return f"User #{self.steam_id}, {self.user_login}. " \
               f"Wallet balance: {bucks:d}.{cents:02d} {self.currency}"


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
