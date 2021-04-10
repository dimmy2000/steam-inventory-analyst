"""Внешние утилиты для работы с предметами сообщества Steam."""
import json

from flask import current_app, flash
from steam.enums import EResult

from webapp.db import db
from webapp.extensions.steam_client import SteamLogin
from webapp.item.models import Description, Item


def get_inventory_contents(db_steam_acc):
    """Загружаем список предметов для выбранного аккаунта из базы."""
    pass


def update_inventory_contents(db_steam_acc):
    """Парсим список предметов сообщества Steam."""
    current_app.logger.info("Update inventory contents function")

    username = db_steam_acc.username
    login_key = db_steam_acc.login_key
    profile = db_steam_acc.steam_id
    account_id = db_steam_acc.account_id

    db_inventory = db.session.query(Item).filter_by(
        account_id=account_id).all()
    client = SteamLogin()

    login_result = client.login(username=username,
                                login_key=login_key)

    # Выводим сообщение с результатом авторизации в лог
    current_app.logger.info(f"Login result: {login_result}")

    if login_result == EResult.OK:
        current_app.logger.info(f"Logged on as: {client.user.name}")
        inventory = client.get_web_session().get(
            'https://steamcommunity.com/profiles/'
            f'{profile}/inventory/json/753/6?l=russian')
        inventory.raise_for_status()
        inventory = inventory.json()
        client.logout()

        items = inventory["rgInventory"]
        descriptions = inventory["rgDescriptions"]

        current_app.logger.info("write items")
        # Пишем в БД перечень имеющихся предметов в инвентаре
        for item in items:
            exists = db.session.query(Item).filter_by(asset_id=item).first() \
                is not None
            current_app.logger.info(f'{item} exist {exists}')
            if not exists:
                db_item = Item(
                    asset_id=int(item),
                    class_id=int(items[item]['classid']),
                    account_id=account_id,
                )
                db.session.add(db_item)

        current_app.logger.info("delete stale items")
        # Если в БД есть предмет, которого нет в инвентаре - удаляем
        for item in db_inventory:
            if str(item.asset_id) not in items:
                current_app.logger.info(f"delete {item.asset_id}")
                db.session.delete(item)

        current_app.logger.info("write descriptions")
        tags = {}
        for class_id in descriptions:
            exists = db.session.query(Description).filter_by(
                class_id=class_id).first() is not None
            current_app.logger.info(f"{descriptions[class_id]['classid']} exist {exists}")
            if not exists:
                # Перечень тэгов для записи в БД
                categories = [
                    "Редкость",
                    "Игра",
                    "Оформление карточки",
                    "Тип предмета",
                ]
                # Собираем тэги в отдельный словарь для удобства
                key = descriptions[class_id]["classid"]
                tags[key] = {}
                for category in categories:
                    for tag in descriptions[class_id]['tags']:
                        if tag['category_name'] == category:
                            tags[key][category] = tag['name']

                classid = descriptions[class_id]["classid"]
                appid = descriptions[class_id]["appid"]
                icon_url_large = descriptions[class_id][
                    "icon_url_large"]
                market_hash_name = descriptions[class_id][
                    "market_hash_name"]
                type_ = descriptions[class_id]["type"]
                value = descriptions[class_id]["descriptions"][0]["value"]
                rarity = tags[classid]["Редкость"]
                game = tags[classid]["Игра"]
                item_type = tags[classid]["Тип предмета"]
                card_border = tags[classid]["Оформление карточки"] \
                    if "Оформление карточки" in tags[classid].keys() else None

                db_description = Description(
                    class_id=classid,
                    app_id=appid,
                    icon_url_large=icon_url_large,
                    market_hash_name=market_hash_name,
                    item_type=type_,
                    value=value,
                    rarity_tag=rarity,
                    game_tag=game,
                    item_type_tag=item_type,
                    card_border_tag=card_border,
                )
                db.session.add(db_description)
        db.session.commit()
    else:
        flash(f'Сессия {db_steam_acc.username} истекла. Нужна повторная '
              f'авторизация', 'light')
