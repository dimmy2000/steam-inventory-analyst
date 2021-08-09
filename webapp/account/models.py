"""Модель таблицы авторизованных аккаунтов."""
from sqlalchemy.orm import relationship

from webapp.db import db


class Account(db.Model):
    """Модель таблицы привязанных аккаунтов Steam.

    Хранит идентификационный номер профиля в БД, идентификационный номер
    профиля на сервисах Steam, логин профиля, логин-токен для входа без пароля,
    sentry-файл для входа без 2FA-кода, ссылку на аватар профиля, никнейм
    профиля, баланс кошелька, валюту кошелька и идентификационный номер
    пользователя, которому принадлежит профиль.
    """

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
    items = relationship("Item", cascade="all,delete", backref='accounts',
                         lazy="dynamic")

    def __repr__(self):
        """Определяем формат вывода объекта класса Account."""
        return f"Account {self.username}."
