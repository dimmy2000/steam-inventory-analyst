"""Модель таблицы авторизованных воркеров."""
from webapp.db import db


class Worker(db.Model):
    """Модель таблицы привязанных аккаунтов Steam."""

    __tablename__ = "workers"

    steam_id = db.Column(db.BigInteger, unique=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    login_key = db.Column(db.String, unique=True)
    avatar_url = db.Column(db.String)
    wallet_balance = db.Column(db.Integer)
    currency = db.Column(db.String(3))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        """Определяем формат вывода объекта класса Worker."""
        return f"Worker {self.steam_id}, {self.username}."
