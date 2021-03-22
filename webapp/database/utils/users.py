"""Здесь покоятся методы работы с таблицей авторизованных пользователей."""
import logging

from webapp.database import db_session
from webapp.database.models import User


def create_user(steam_id, user_login, avatar_url, wallet_balance, currency):
    """Добавляем пользователя в таблицу.

    Если пользователь уже существует - перезаписываем данные, которые
    нуждаются в обновлении.

    """
    try:
        user = User.query.filter(User.steam_id == steam_id).first()
        if user:
            logging.info(f"Профиль пользователя {user_login} имеется в базе")

            # Создаем список столбцов с изменяемым содержимым
            columns = User.__table__.c.keys()
            comparison_attr = 'unique'
            list_ = [column for column in columns if getattr(
                getattr(User.__table__.c, column),
                comparison_attr) is None]
            logging.debug(list_)

            for attr in list_:
                if getattr(user, attr) != eval(attr):
                    logging.debug("at first")
                    logging.debug(f"User {attr} is: {getattr(user, attr)}")
                    logging.debug("but then")
                    setattr(user, attr, eval(attr))
                    logging.debug(f"User {attr} is: {getattr(user, attr)}")
            db_session.commit()

        else:
            logging.info("Создаем профиль пользователя %s", user_login)
            user = User(steam_id=steam_id, user_login=user_login,
                        avatar_url=avatar_url, wallet_balance=wallet_balance,
                        currency=currency)
            db_session.add(user)
            db_session.commit()
    except Exception as err:
        logging.info(type(err))
        logging.info(err)
    finally:
        logging.info(user)


def delete_user(steam_id):
    """Удаляем пользователя из таблицы."""
    user = User.query.filter(User.steam_id == steam_id).first()
    db_session.delete(user)
    db_session.commit()
    logging.info(user)


def take_user():
    """Берем пользователя из таблицы и выкидываем в консоль."""
    user = User.query.first()
    logging.info(user)


def update_user(user, something):
    """Обновляем данные пользователя."""
    user = User.query.first()
    user.something = 'updated_value'
    db_session.commit()


if __name__ == '__main__':
    logging.basicConfig(filename='../../steam_stat.log',
                        filemode='a',
                        encoding='utf-8',
                        format="%(asctime)s | %(levelname)s | %(message)s",
                        datefmt='%d-%m-%Y %H:%M:%S',
                        level=logging.INFO)

    create_user(12345678901234567, "user_login", "avatar", 10100, "RUB")
