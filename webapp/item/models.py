"""Модель таблиц связанных с отображением предметов сообщества Steam."""
from sqlalchemy.orm import relationship

from webapp.db import db


class Item(db.Model):
    """Модель таблицы предметов в инвентаре Steam.

    Хранит идентификационный номер предмета в базе, идентификационный номер
    предмета на серверах Steam, идентификационный номер описания предмета,
    идентификационные номер аккаунта-владельца предмета.
    """

    __tablename__ = "items"

    item_id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.BigInteger, index=True)
    class_id = db.Column(db.Integer, db.ForeignKey('descriptions.class_id'))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'))
    descriptions = relationship("Description", backref='items', lazy="joined")

    def __repr__(self):
        """Определяем формат вывода объекта класса Item."""
        return f"Item # {self.asset_id}."


class Description(db.Model):
    """Модель таблицы описаний предметов сообщества Steam.

    Хранит идентификационный номер описания, идентификационный номер
    приложения, идентификатор иконки предмета, имя предмета на торговой
    площадке, имя предмета для вывода, тип предмета, описание предмета,
    список тегов: редкость, игра, тип предмета, тип коллекционной карточки.
    """

    __tablename__ = "descriptions"

    class_id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.SmallInteger)
    icon_url_large = db.Column(db.String)
    market_hash_name = db.Column(db.String)
    market_name = db.Column(db.String)
    item_type = db.Column(db.String)
    value = db.Column(db.String)
    rarity_tag = db.Column(db.String)
    game_tag = db.Column(db.String)
    item_type_tag = db.Column(db.String)
    card_border_tag = db.Column(db.String)

    def __repr__(self):
        """Определяем формат вывода объекта класса Description."""
        return f"Description for {self.market_hash_name}."
