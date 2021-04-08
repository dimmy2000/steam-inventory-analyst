"""Внешние утилиты для работы с подключенными аккаунтами."""
import logging

from flask import current_app, flash, redirect, url_for
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from steam.client import SteamClient
from steam.enums import ECurrencyCode, EResult
from steam.enums.emsg import EMsg

from webapp.account.models import Account
from webapp.db import db


class SteamLogin(SteamClient):
    """Переопределяем базовый класс SteamClient."""

    sentry = None
    wallet_balance = None
    currency = None

    def __init__(self):
        """Создаем свой хандлер информации о балансе кошелька."""
        super().__init__()
        self.on(EMsg.ClientWalletInfoUpdate, self._get_wallet_balance)

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
            logging.debug("Sentry is: %s" % sentry_bytes)
            return True
        except IOError as e:
            self._LOG.error("Store_sentry: %s" % str(e))

        return False

    def get_sentry(self, username):
        """Return contents of sentry file for the given username.

        .. note::
            returns ``None`` if :attr:`credential_location` is not set, or
            file is not found/inaccessible

        :param username: username
        :type  username: str
        :return: sentry file contents, or ``None``
        :rtype: :class:`bytes`, :class:`None`
        """
        account = db.session.query(Account).filter_by(
            username=username).first()
        if account:
            self.sentry = account.sentry
            logging.debug("Got sentry: %s" % self.sentry)
            return self.sentry
        return None

    def _get_wallet_balance(self, msg):
        """Получаем баланс кошелька и пишем его в БД."""
        logging.info("Get wallet balance function")
        self.wallet_balance = msg.body.balance64
        self.currency = ECurrencyCode(msg.body.currency).name
        logging.info(f"Balance: {self.wallet_balance//100}."
                     f"{self.wallet_balance%100} {self.currency}")


def auth_attempt(user_id,
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
    current_app.logger.info("Auth attempt function")
    client = SteamLogin()

    login_result = client.login(username=username,
                                password=password,
                                auth_code=auth_code,
                                two_factor_code=two_factor_code)

    # Создаем сообщение с результатом авторизации для вывода в лог
    current_app.logger.info(f"Login result: {login_result}")

    if login_result == EResult.OK:
        # В случае успешной авторизации пишем полученные данные в БД
        flash(f'Logged on as {username}', 'info')
        current_app.logger.info(f'Logged on as {username}')
        current_app.logger.debug("Got sentry: %s" % client.sentry)

        steam_id = int(client.steam_id)
        avatar_url = client.user.get_avatar_url(2)
        login_key = client.login_key
        sentry = client.sentry
        nickname = client.user.name
        wallet_balance = client.wallet_balance
        currency = client.currency

        save_acc_info(
            user_id=user_id,
            username=username,
            steam_id=steam_id,
            login_key=login_key,
            sentry=sentry,
            avatar_url=avatar_url,
            nickname=nickname,
            wallet_balance=wallet_balance,
            currency=currency,
        )

        client.disconnect()
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

    client.disconnect()
    return False


def save_acc_info(user_id, username, **kwargs):
    """Добавляем подключенный аккаунт Steam в БД.

    Если аккаунт уже существует - обновляем данные, которые изменились.
    """
    current_app.logger.info("Save account info function")
    # Создаем список переменных переданных функции
    attributes = {}
    for key, value in kwargs.items():
        attributes[key] = value

    steam_acc = db.session.query(Account).filter_by(
        username=username).first()

    if steam_acc:
        current_app.logger.info(f"Account {username} already exists. "
                                f"Trying to update data.")
        for attribute, value in attributes.items():
            # Если содержимое ячейки изменилось - перезаписываем его
            if value is not None:
                if getattr(steam_acc, attribute) != value:
                    current_app.logger.info(
                        f"Old account {attribute} is: "
                        f"{getattr(steam_acc, attribute)}")
                    setattr(steam_acc, attribute, value)
                    current_app.logger.info(
                        f"New account {attribute} is: "
                        f"{getattr(steam_acc, attribute)}")
    else:
        current_app.logger.info("Create account %s", username)
        steam_acc = Account(
            username=username,
            user_id=user_id,
        )
        for attribute, value in attributes.items():
            setattr(steam_acc, attribute, value)
        db.session.add(steam_acc)
    db.session.commit()
    current_app.logger.info("Successful DB injection")


def update_acc_info(db_steam_acc):
    """Обновляем информацию об аккаунте в таблице."""
    current_app.logger.info("Update account info function")
    steam_account = SteamLogin()

    login_result = steam_account.login(username=db_steam_acc.username,
                                       login_key=db_steam_acc.login_key)

    # Создаем сообщение с результатом авторизации для вывода в лог
    current_app.logger.info(f"Login result: {login_result}")

    if login_result == EResult.OK:
        current_app.logger.info(f"Logged on as: {steam_account.user.name}")
        # Получаем данные об аккаунте
        avatar_url = steam_account.user.get_avatar_url(2)
        nickname = steam_account.user.name
        wallet_balance = steam_account.wallet_balance
        currency = steam_account.currency
        sentry = steam_account.sentry
        # Пишем полученные данные в базу
        db_steam_acc.avatar_url = avatar_url
        db_steam_acc.nickname = nickname
        db_steam_acc.wallet_balance = wallet_balance
        db_steam_acc.currency = currency
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
              f'авторизация', 'light')
