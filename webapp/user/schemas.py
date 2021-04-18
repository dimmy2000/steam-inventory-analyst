"""Схемы для работы с marshmallow."""
from marshmallow import post_load, fields

from webapp.db import ma
from webapp.user.models import User


class UserSchema(ma.SQLAlchemySchema):
    """Создает схему marshmallow из модели sqlalchemy."""

    class Meta:
        """Загружает модель sqlalchemy."""

        model = User

    user_id = fields.Integer()
    username = fields.String()
    email = fields.String()
    password_hash = fields.String()
    last_seen = fields.DateTime()

    @post_load
    def make_user(self, data, **kwargs):
        """Функция для десериализации объекта."""
        return User(**data)


user_schema = UserSchema()
