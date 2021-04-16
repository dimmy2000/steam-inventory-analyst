"""Docstring which is missing."""
from flask import current_app, flash
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from steam.enums import EResult

from webapp import celery
from webapp.account.models import Account
from webapp.account.schemas import account_schema
from webapp.db import db
from webapp.extensions.steam_client import SteamLogin


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
    db_steam_acc = db.session.query(Account).filter_by(
        username=username, user_id=user_id).first()

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


@celery.task(name="account.update_info")
def update_acc_info(db_steam_acc):
    """Обновляем информацию об аккаунте в таблице."""
    current_app.logger.info("Update account info function")
    # Преобразуем полученный словарь обратно в модель sqlalchemy
    db_steam_acc = account_schema.load(db_steam_acc)

    client = SteamLogin()

    login_result = client.login(
        username=db_steam_acc.username,
        login_key=db_steam_acc.login_key,
    )

    # Создаем сообщение с результатом авторизации для вывода в лог
    current_app.logger.info(f"Login result: {login_result}")

    if login_result == EResult.OK:
        current_app.logger.info(f"Logged on as: {client.user.name}")
        # Получаем данные об аккаунте
        user_id = db_steam_acc.user_id
        username = db_steam_acc.username
        avatar_url = client.user.get_avatar_url(2)
        nickname = client.user.name
        wallet_balance = client.wallet_balance
        currency = client.currency
        client.logout()

        # Пишем полученные данные в базу
        save_acc_info.delay(
            user_id=user_id,
            username=username,
            avatar_url=avatar_url,
            nickname=nickname,
            wallet_balance=wallet_balance,
            currency=currency,
        )
    else:
        flash(f'Сессия {db_steam_acc.username} истекла. Нужна повторная '
              f'авторизация', 'light')
