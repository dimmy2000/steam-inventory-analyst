"""Docstring which is missing."""
from flask import current_app

from webapp import celery

from webapp.account.models import Account
from webapp.db import db


@celery.task(serializer="msgpack")
def save_acc_info(user_id, username, **kwargs):
    """Добавляем подключенный аккаунт Steam в БД.

    Если аккаунт уже существует - обновляем данные, которые изменились.
    """
    current_app.logger.info("Save account info function")
    # Создаем список аргументов переданных функции
    args = {}
    for key, value in kwargs.items():
        args[key] = value

    db_steam_acc = db.session.query(Account).filter_by(
        username=username).first()

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
        db.session.add(db_steam_acc)
    db.session.commit()
    current_app.logger.info("Successful DB injection")
