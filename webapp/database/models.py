"""Здесь покоятся модели баз данных."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Worker(db.Model):
    """Модель таблицы привязанных аккаунтов Steam."""

    __tablename__ = "workers"

    worker_id = db.Column(db.BigInteger, unique=True, primary_key=True)
    user_login = db.Column(db.String, unique=True, nullable=False)
    avatar_url = db.Column(db.String, nullable=False)
    wallet_balance = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):
        """Определяем формат вывода объекта класса Worker."""
        return f"Worker #{self.steam_id}, {self.user_login}."
