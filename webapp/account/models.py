"""Модель таблицы авторизованных аккаунтов."""
from sqlalchemy.orm import relationship

from webapp.db import db


class Account(db.Model):
    """Модель таблицы привязанных аккаунтов Steam."""

    __tablename__ = "accounts"

    account_id = db.Column(db.Integer, primary_key=True)
    steam_id = db.Column(db.BigInteger, index=True)
    username = db.Column(db.String, index=True, nullable=False)
    login_key = db.Column(db.String, unique=True)
    sentry = db.Column(db.LargeBinary)
    avatar_url = db.Column(db.String)
    nickname = db.Column(db.String)
    wallet_balance = db.Column(db.Integer)
    currency = db.Column(db.String(3))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    items = relationship("Item", lazy="joined")
    hashes = relationship("Hash", lazy="joined")

    def __repr__(self):
        """Определяем формат вывода объекта класса Account."""
        return f"Account {self.username}."


class Hash(db.Model):
    """Модель таблицы хэшей данных об аккаунтах Steam."""

    __tablename__ = "hashes"

    hash_id = db.Column(db.Integer, primary_key=True)
    account_hash = db.Column(db.BINARY(128))
    account_last_updated = db.Column(db.DateTime)
    inventory_hash = db.Column(db.BINARY(128))
    inventory_last_updated = db.Column(db.DateTime)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'))

    def __repr__(self):
        """Определяем формат вывода объекта класса Hash."""
        return f"Hash id: {self.hash_id}."
