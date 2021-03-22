"""Здесь покоятся модели баз данных."""
from datetime import datetime

from flask_login import UserMixin

from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import check_password_hash, generate_password_hash

from flask_login._compat import text_type

db = SQLAlchemy()


class Mixin(UserMixin):
    """Переопределяем метод класса для получения id."""

    def get_id(self):
        try:
            return text_type(self.user_id)
        except AttributeError:
            raise NotImplementedError('No `user_id` attribute - override '
                                      '`get_id`')


class User(Mixin, db.Model):
    """Модель таблицы пользователей `users`."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Определяем формат вывода объекта класса User."""
        return f"<User {self.username}>"


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
