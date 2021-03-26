"""Дополнительные утилиты для работы с воркерами."""
import logging

from webapp import Worker, db


def create_worker(steam_id, username, user_id, login_key=None, avatar_url=None,
                  wallet_balance=0, currency=""):
    """Добавляем воркер в таблицу.

    Если воркер уже существует - перезаписываем данные, которые
    нуждаются в обновлении.

    """
    try:
        worker = Worker.query.filter_by(steam_id=steam_id).first()
        if worker:
            # Создаем список столбцов с изменяемым содержимым
            columns = Worker.__table__.c.keys()
            comparison_attr = 'unique'
            col_names = [column for column in columns if getattr(
                getattr(Worker.__table__.c, column),
                comparison_attr) is None]
            logging.debug(col_names)

            for col_name in col_names:
                if getattr(worker, col_name) != eval(col_name):
                    logging.debug("at first")
                    logging.debug(
                        f"User {col_name} is: {getattr(worker, col_name)}")
                    logging.debug("but then")
                    try:
                        setattr(worker, col_name, eval(col_name))
                    except Exception as err:
                        logging.info(type(err), err)
                    logging.debug(
                        f"User {col_name} is: {getattr(worker, col_name)}")
            db.session.commit()

        else:
            logging.info("Создаем worker %s", username)
            worker = Worker(steam_id=steam_id, username=username,
                            login_key=login_key, avatar_url=avatar_url,
                            wallet_balance=wallet_balance,
                            currency=currency, user_id=user_id)
            db.session.add(worker)
            db.session.commit()
    except Exception as err:
        logging.info(type(err))
        logging.info(err)