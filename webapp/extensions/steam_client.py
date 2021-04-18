"""Сущность для взаимодействия с сервисами Steam."""
import logging

from steam.client import SteamClient
from steam.enums import ECurrencyCode
from steam.enums.emsg import EMsg

from webapp.account.models import Account
from webapp.db import db


class SteamLogin(SteamClient):
    """Переопределяем базовый класс SteamClient."""

    sentry = None

    def __init__(self):
        """Создаем хандлер информации о балансе кошелька."""
        super().__init__()
        self.wallet_balance = None
        self.currency = None

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
