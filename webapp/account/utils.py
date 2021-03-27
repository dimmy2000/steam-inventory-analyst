"""Дополнительные утилиты для работы с воркерами."""
import logging

from webapp import Account, db


def create_worker(steam_id, username, user_id, login_key=None, avatar_url=None,
                  wallet_balance=0, currency=""):
    """Добавляем подключенный аккаунт Steam в БД.

    Если аккаунт уже существует - перезаписываем данные, которые
    нуждаются в обновлении.

    """
    try:
        steam_acc = Account.query.filter_by(steam_id=steam_id).first()
        if steam_acc:
            # Создаем список столбцов с изменяемым содержимым
            columns = Account.__table__.c.keys()
            comparison_attr = 'unique'
            col_names = [column for column in columns if getattr(
                getattr(Account.__table__.c, column),
                comparison_attr) is None]
            logging.debug(col_names)

            for col_name in col_names:
                if getattr(steam_acc, col_name) != eval(col_name):
                    logging.debug("at first")
                    logging.debug(
                        f"User {col_name} is: {getattr(steam_acc, col_name)}")
                    logging.debug("but then")
                    try:
                        setattr(steam_acc, col_name, eval(col_name))
                    except Exception as err:
                        logging.info(type(err), err)
                    logging.debug(
                        f"User {col_name} is: {getattr(steam_acc, col_name)}")
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