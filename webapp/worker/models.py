"""Модель таблицы авторизованных воркеров."""
from sqlalchemy.testing.plugin.plugin_base import logging

from webapp.db import db


class Worker(db.Model):
    """Модель таблицы привязанных аккаунтов Steam."""

    __tablename__ = "workers"

    steam_id = db.Column(db.BigInteger, unique=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    login_key = db.Column(db.String, unique=True)
    avatar_url = db.Column(db.String, nullable=False)
    wallet_balance = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))


    def create_worker(self, steam_id, workername, login_key, avatar_url,
                      wallet_balance, currency):
        """Добавляем воркер в таблицу.

        Если воркер уже существует - перезаписываем данные, которые
        нуждаются в обновлении.

        """
        try:
            worker = self.query.filter(self.steam_id == steam_id).first()
            if worker:
                logging.info(
                    f"Профиль пользователя {workername} имеется в базе")

                # Создаем список столбцов с изменяемым содержимым
                columns = self.__table__.c.keys()
                comparison_attr = 'unique'
                list_ = [column for column in columns if getattr(
                    getattr(self.__table__.c, column),
                    comparison_attr) is None]
                logging.debug(list_)

                for attr in list_:
                    if getattr(worker, attr) != eval(attr):
                        logging.debug("at first")
                        logging.debug(
                            f"User {attr} is: {getattr(worker, attr)}")
                        logging.debug("but then")
                        setattr(worker, attr, eval(attr))
                        logging.debug(
                            f"User {attr} is: {getattr(worker, attr)}")
                db.session.commit()

            else:
                logging.info("Создаем профиль пользователя %s", workername)
                worker = Worker(steam_id=steam_id, username=workername,
                                login_key=login_key, avatar_url=avatar_url,
                                wallet_balance=wallet_balance,
                                currency=currency)
                db.session.add(worker)
                db.session.commit()
        except Exception as err:
            logging.info(type(err))
            logging.info(err)
        finally:
            logging.info(worker)

    def __repr__(self):
        """Определяем формат вывода объекта класса Worker."""
        return f"Worker #{self.steam_id}, {self.username}."
