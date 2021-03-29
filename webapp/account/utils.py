"""Дополнительные утилиты для работы с воркерами."""
import logging

from webapp import Account, db


def save_acc_info(username, user_id, steam_id, login_key, avatar_url,
                  wallet_balance, currency):
    """Добавляем подключенный аккаунт Steam в БД.

    Если аккаунт уже существует - перезаписываем данные, которые
    нуждаются в обновлении.

    """
    try:
        steam_acc = Account.query.filter_by(username=username).first()
        if steam_acc:
            # Создаем список столбцов с изменяемым содержимым
            columns = ["avatar_url", "wallet_balance", "currency"]

            for column in columns:
                # если содержимое ячейки обновилось - перезаписываем
                if getattr(steam_acc, column) != eval(column):
                    logging.info("at first")
                    logging.info(
                        f"User {column} is: {getattr(steam_acc, column)}")
                    logging.info("but then")
                    try:
                        setattr(steam_acc, column, eval(column))
                    except Exception as err:
                        logging.info(type(err), err)
                    logging.info(
                        f"User {column} is: {getattr(steam_acc, column)}")
            db.session.commit()

        else:
            logging.info("Создаем account %s", username)
            steam_acc = Account(steam_id=steam_id, username=username,
                                login_key=login_key, avatar_url=avatar_url,
                                wallet_balance=wallet_balance,
                                currency=currency, user_id=user_id)
            db.session.add(steam_acc)
            db.session.commit()
    except Exception as err:
        logging.info(type(err))
        logging.info(err)
