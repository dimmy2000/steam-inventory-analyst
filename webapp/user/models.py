"""Модель таблицы авторизованных пользователей."""
from datetime import datetime
from hashlib import md5

from flask_login import UserMixin
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from webapp.db import db


class Mixin(UserMixin):
    """Переопределяем метод класса `UserMixin` для получения `id`."""

    def get_id(self):
        """Меняем ожидаемый ярлык столбца с `id` на `user_id`."""
        try:
            return str(self.user_id)
        except AttributeError:
            raise NotImplementedError('No `user_id` attribute - override '
                                      '`get_id`')


class User(Mixin, db.Model):
    """Модель таблицы пользователей `users`.

    Хранит идентификационный номер пользователя, имя пользователя, адрес
    электронной почты, хэш пароля и время последнего входа.

    """

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    accounts = relationship("Account", cascade="all,delete", backref='users', lazy="dynamic")

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def set_password(self, password):
        """Создаем хеш пароля."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверяем хеш пароля."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Определяем формат вывода объекта класса User."""
        return f"<User {self.username}>"
