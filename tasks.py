"""Асинхронные задачи Celery."""
from flask import current_app
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

from webapp import celery
from webapp.account.models import Account
from webapp.account.schemas import account_schema
from webapp.db import db
from webapp.item.models import Description, Item


@celery.task(name="account.save_info")
def save_acc_info(user_id, username, **kwargs):
    """Добавляем подключенный аккаунт Steam в БД.

    Если аккаунт уже существует - обновляем данные, которые изменились.
    """
    current_app.logger.info("Save account info function")
    # Создаем список аргументов переданных функции
    args = {}
    for key, value in kwargs.items():
        args[key] = value
    db_steam_acc = Account.query.filter_by(username=username,
                                           user_id=user_id).first()

    if db_steam_acc:
        current_app.logger.info(f"Account {username} already exists. "
                                f"Trying to update data.")
        for arg, value in args.items():
            # Если содержимое ячейки изменилось - перезаписываем его
            if value is not None:
                if getattr(db_steam_acc, arg) != value:
                    current_app.logger.info(
                        f"Old account {arg} is: "
                        f"{getattr(db_steam_acc, arg)}")
                    setattr(db_steam_acc, arg, value)
                    current_app.logger.info(
                        f"New account {arg} is: "
                        f"{getattr(db_steam_acc, arg)}")
    else:
        current_app.logger.info("Create account %s", username)
        db_steam_acc = Account(
            username=username,
            user_id=user_id,
        )
        for arg, value in args.items():
            setattr(db_steam_acc, arg, value)
        try:
            db.session.add(db_steam_acc)
        except (DBAPIError, SQLAlchemyError) as err:
            current_app.logger.info(err)
    db.session.commit()
    current_app.logger.info("Successful DB injection")
    return None


@celery.task(name="account.save_items")
def save_items(db_acc_json, items):
    """Пишем в БД перечень имеющихся предметов в инвентаре."""
    current_app.logger.info("write items")

    # Преобразуем полученный словарь обратно в модель sqlalchemy
    db_steam_acc = account_schema.load(db_acc_json)

    account_id = db_steam_acc.account_id
    db_inventory = Item.query.filter_by(account_id=account_id).all()

    # Сохраняем данные о предметах в инвентаре в БД
    for item in items:
        exists = Item.query.filter_by(asset_id=item).first() is not None
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
    db.session.commit()


@celery.task(name="account.save_descriptions")
def save_descriptions(descriptions):
    """Добавляем в БД описания предметов, которых там нет."""
    current_app.logger.info("write descriptions")

    tags = {}
    # Наличие описания в БД проверяется по уникальному ключу classid
    for class_id in descriptions:
        exists = Description.query.filter_by(
            class_id=int(descriptions[class_id][
                         'classid'])).first() is not None
        current_app.logger.info(f"{descriptions[class_id]['classid']} "
                                f"exist {exists}")
        if not exists:
            # Перечень тэгов для записи в БД
            categories = [
                "Редкость",
                "Игра",
                "Оформление карточки",
                "Тип предмета",
            ]

            classid = int(descriptions[class_id]["classid"])
            appid = int(descriptions[class_id]["appid"])
            icon_url_large = descriptions[class_id][
                "icon_url_large"]
            market_hash_name = descriptions[class_id][
                "market_hash_name"]
            market_name = descriptions[class_id][
                "market_name"]
            type_ = descriptions[class_id]["type"]
            value = descriptions[class_id]["descriptions"][0]["value"]

            # Собираем тэги в отдельный словарь для удобства
            tags[classid] = {}
            for category in categories:
                for tag in descriptions[class_id]['tags']:
                    if tag['category_name'] == category:
                        tags[classid][category] = tag['name']

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
                market_name=market_name,
                item_type=type_,
                value=value,
                rarity_tag=rarity,
                game_tag=game,
                item_type_tag=item_type,
                card_border_tag=card_border,
            )
            db.session.add(db_description)
    db.session.commit()
