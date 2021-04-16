"""Схемы для работы с marshmallow."""
from marshmallow import fields, post_load

from webapp.db import ma
from webapp.item.models import Description, Item


class ItemSchema(ma.SQLAlchemySchema):
    """Создает схему marshmallow из модели sqlalchemy."""

    class Meta:
        """Загружает модель sqlalchemy."""

        model = Item

    item_id = fields.Integer()
    asset_id = fields.Integer()
    class_id = fields.Integer()
    account_id = fields.Integer()

    @post_load
    def make_item(self, data, **kwargs):
        """Функция для десериализации объекта."""
        return Item(**data)


class DescriptionSchema(ma.SQLAlchemySchema):
    """Создает схему marshmallow из модели sqlalchemy."""

    class Meta:
        """Загружает модель sqlalchemy."""

        model = Description

    class_id = fields.Integer()
    app_id = fields.Integer()
    icon_url_large = fields.String()
    market_hash_name = fields.String()
    market_name = fields.String()
    item_type = fields.String()
    value = fields.String()
    rarity_tag = fields.String()
    game_tag = fields.String()
    item_type_tag = fields.String()
    card_border_tag = fields.String()

    @post_load
    def make_description(self, data, **kwargs):
        """Функция для десериализации объекта."""
        return Description(**data)


item_schema = ItemSchema()
items_schema = ItemSchema(many=True)
description_schema = DescriptionSchema()
