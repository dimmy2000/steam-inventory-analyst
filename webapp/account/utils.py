"""Внешние утилиты для работы с подключенными аккаунтами."""
import logging

from flask import flash, redirect, url_for, current_app
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from steam.client import SteamClient
from steam.enums import ECurrencyCode, EResult
from steam.enums.emsg import EMsg

from webapp.account.models import Account
from webapp.db import db


class SteamLogin(SteamClient):
    """Переопределяем базовый класс SteamClient."""

    sentry = None

    def store_sentry(self, username, sentry_bytes):
        """Store sentry bytes under a username.

        :param username: username
        :type  username: str
        :param sentry_bytes:
        :type  sentry_bytes: bytes
        :return: Whenever the operation succeed
        :rtype: :class:`bool`
        """
        try:
            self.sentry = sentry_bytes
            current_app.logger.info("sentry is: %s" % sentry_bytes)
            return True
        except IOError as e:
            self._LOG.error("store_sentry: %s" % str(e))

        return False


def auth_attempt(user,
                 username,
                 password,
                 auth_code=None,
                 two_factor_code=None):
    """Авторизация на серверах Steam.

    По полученным учетным данным делаем попытку авторизации с помощью
    SteamClient(). При успешном входе пишем полученные данные о пользователе
    в БД с помощью функции save_acc_info и возвращаем True. В случае неудачной
    авторизации обрабатываем возможные запросы ввода дополнительных данных.
    В случае невозможности устранения причин отказа в авторизации возвращаем
    False.
    """
    current_app.logger.info("Got into auth attempt function")
    client = SteamLogin()

    login_result = client.login(username=username,
                                password=password,
                                auth_code=auth_code,
                                two_factor_code=two_factor_code)

    # Создаем сообщение с результатом авторизации для вывода в лог
    current_app.logger.info(f"Login result: {login_result}")

    if login_result == EResult.OK:
        # В случае успешной авторизации пишем полученные данные в БД
        current_app.logger.info(f"Got: {user}")
        flash(f'Logged on as {username}', 'info')
        current_app.logger.info(f'Logged on as {username}')
        current_app.logger.info("Got sentry: %s" % client.sentry)

        steam_id = int(client.steam_id)
        avatar_url = client.user.get_avatar_url(2)
        login_key = client.login_key
        sentry = client.sentry
        user_id = user.user_id

        save_acc_info(steam_id=steam_id,
                      username=username,
                      login_key=login_key,
                      sentry=sentry,
                      avatar_url=avatar_url,
                      user_id=user_id)

        return True

    elif login_result == EResult.InvalidPassword:
        flash('Invalid password', 'EResult')
        current_app.logger.info('Invalid password')
        return redirect(url_for('account.make_session'))

    elif login_result in (EResult.AccountLogonDenied,
                          EResult.InvalidLoginAuthCode):
        flash("Enter email code", 'EResult')
        current_app.logger.info("Enter email code")

    elif login_result in (EResult.AccountLoginDeniedNeedTwoFactor,
                          EResult.TwoFactorCodeMismatch):
        flash('Enter 2FA-code', 'EResult')
        current_app.logger.info('Enter 2FA-code')

    return False


def save_acc_info(user_id, username, login_key, steam_id, avatar_url, sentry):
    """Добавляем подключенный аккаунт Steam в БД.

    Если аккаунт уже существует - перезаписываем данные, которые могли
    измениться.

    """
    current_app.logger.info("Got into save account info function")
    try:
        steam_acc = db.session.query(Account).filter_by(
            username=username,
            user_id=user_id).first()

        if steam_acc:
            current_app.logger.info(f"Аккаунт {username} имеется в БД. Попытка обновить "
                        f"данные")
            # Создаем список столбцов, содержимое которых надо обновить
            columns = {"avatar_url": avatar_url,
                       "login_key": login_key,
                       "sentry": sentry}

            for column in columns.keys():
                # Если содержимое ячейки изменилось - перезаписываем его
                if getattr(steam_acc, column) != columns[column]:
                    current_app.logger.info(
                        f"Old account {column} is: "
                        f"{getattr(steam_acc,column)}")
                    setattr(steam_acc, column, columns[column])
                    current_app.logger.info(
                        f"New account {column} is: "
                        f"{getattr(steam_acc, column)}")
            db.session.commit()

        else:
            current_app.logger.info("Создаем account %s", username)
            steam_acc = Account(steam_id=steam_id,
                                username=username,
                                login_key=login_key,
                                avatar_url=avatar_url,
                                sentry=sentry,
                                user_id=user_id)
            db.session.add(steam_acc)
            db.session.commit()
            current_app.logger.info("Запись в БД прошла успешно")
    except (DBAPIError, SQLAlchemyError) as err:
        flash(err, 'info')
        current_app.logger.info(type(err))
        current_app.logger.info(err)


def update_acc_info(db_steam_acc):
    """Обновляем информацию об аккаунте в таблице."""
    current_app.logger.info("Got into update account info function")
    steam_account = SteamLogin()

    @steam_account.on(EMsg.ClientWalletInfoUpdate)
    def get_wallet_balance(msg):
        """Получаем баланс кошелька и пишем его в БД."""
        current_app.logger.info("Got into get wallet balance function")
        wallet_balance = msg.body.balance64
        currency = ECurrencyCode(msg.body.currency).name
        current_app.logger.info(f"balance: {wallet_balance} {currency}")
        db_steam_acc.wallet_balance = wallet_balance
        db_steam_acc.currency = currency
        db.session.add(db_steam_acc)
        db.session.commit()

    login_result = steam_account.login(username=db_steam_acc.username,
                                       login_key=db_steam_acc.login_key)

    # Создаем сообщение с результатом авторизации для вывода в лог
    current_app.logger.info(f"Login result: {login_result}")

    if login_result == EResult.OK:
        current_app.logger.info(f"Logged on as: {steam_account.user.name}")
        # Получаем данные об аккаунте
        avatar_url = steam_account.user.get_avatar_url(2)
        nickname = steam_account.user.name
        sentry = steam_account.sentry
        # Пишем полученные данные в базу
        db_steam_acc.avatar_url = avatar_url
        db_steam_acc.nickname = nickname
        if db_steam_acc.sentry is None:
            db_steam_acc.sentry = sentry

        try:
            db.session.add(db_steam_acc)
            db.session.commit()
            steam_account.disconnect()
        except (DBAPIError, SQLAlchemyError) as err:
            current_app.logger.info(err)
    else:
        flash(f'Сессия {db_steam_acc.username} истекла. Нужна повторная '
              f'авторизация', 'info')
