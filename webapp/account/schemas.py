"""Схемы для работы с marshmallow."""
from marshmallow import fields, post_load
from marshmallow_sqlalchemy.fields import Nested

from webapp.account.models import Account
from webapp.db import ma
from webapp.item.schemas import ItemSchema


class AccountSchema(ma.SQLAlchemySchema):
    """Создает схему marshmallow из модели sqlalchemy."""

    class Meta:
        """Загружает модель sqlalchemy."""

        model = Account

    account_id = ma.auto_field()
    steam_id = ma.auto_field()
    username = ma.auto_field()
    login_key = ma.auto_field()
    sentry = fields.Raw()
    avatar_url = ma.auto_field()
    nickname = ma.auto_field()
    wallet_balance = ma.auto_field()
    currency = ma.auto_field()
    user_id = ma.auto_field()
    items = Nested(ItemSchema, many=True)

    @post_load
    def make_account(self, data, **kwargs):
        """Функция для десериализации объекта."""
        return Account(**data)


account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)
