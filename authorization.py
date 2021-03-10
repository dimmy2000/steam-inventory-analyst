from binascii import hexlify
from getpass import getpass
import logging
import os
import pickle
import re
from steam.client import SteamClient
import requests
from steam.client.builtins.web import Web
from steam.core.crypto import generate_session_key, symmetric_encrypt
from steam.core.msg import MsgProto
from steam.enums.emsg import EMsg
from steam.enums import EResult
from steam.utils.web import generate_session_id

# настройка логирования
logging.basicConfig(format="%(asctime)s | %(message)s", datefmt='%d-%m-%Y %H:%M:%S', level=logging.DEBUG)
LOG = logging.getLogger()


# переопределяем базовый класс SteamClient, наследуем класс Web чтобы иметь возможность работать с requests
class SteamLogin(SteamClient, Web):
    # указываем путь к папке для хранения персональной информации
    credential_location = "secrets"

    # переопределяем метод из базового класса SteamClient
    def cli_login(self, username='', password='', two_factor_code=None):
        """Generates CLI prompts to complete the login process

        :param username: при необходимости передаем имя пользователя
        :type  username: :class:`str`
        :param password: при необходимости передаем пароль
        :type  password: :class:`str`
        :param two_factor_code: при необходимости передаем код из мобильного приложения
        :type  two_factor_code: :class:`str`
        :return: logon result, see `CMsgClientLogonResponse.eresult
        :rtype: :class:`.EResult`
        """


        if not username:
            username = input("Имя аккаунта Steam: ")
        if not password:
            password = getpass("Пароль: ")
        if not two_factor_code:
            two_factor_code = input("Введите код из мобильного приложения Steam: ")

        auth_code = None
        prompt_for_unavailable = True

        # попытка авторизации с введенными пользовательскими данными
        result = self.login(username, password, None, auth_code, two_factor_code)

        # ловим ошибки
        while result in (EResult.AccountLogonDenied, EResult.InvalidLoginAuthCode,
                         EResult.AccountLoginDeniedNeedTwoFactor, EResult.TwoFactorCodeMismatch,
                         EResult.TryAnotherCM, EResult.ServiceUnavailable,
                         EResult.InvalidPassword,
                         ):
            self.sleep(0.1)

            # введен направильный пароль
            if result == EResult.InvalidPassword:
                password = getpass("Invalid password for %s. Enter password: " % repr(username))

            # требуется код из е-мэйла
            elif result in (EResult.AccountLogonDenied, EResult.InvalidLoginAuthCode):
                prompt = ("Enter email code: " if result == EResult.AccountLogonDenied else
                          "Incorrect code. Enter email code: ")
                auth_code, two_factor_code = input(prompt), None

            # требуется код из мобильного приложения
            elif result in (EResult.AccountLoginDeniedNeedTwoFactor, EResult.TwoFactorCodeMismatch):
                prompt = ("Введите 2FA-код: " if result == EResult.AccountLoginDeniedNeedTwoFactor else
                          "Код введен неверно... Попробуйте еще раз: ")
                auth_code, two_factor_code = None, input(prompt)

            # сервис недоступен
            elif result in (EResult.TryAnotherCM, EResult.ServiceUnavailable):
                if prompt_for_unavailable and result == EResult.ServiceUnavailable:
                    while True:
                        answer = input("Steam is down. Keep retrying? [y/n]: ").lower()
                        if answer in 'yn': break

                    prompt_for_unavailable = False
                    if answer == 'n': break

                # устанавливаем задержку для переподключения
                self.reconnect(maxdelay=15)

            # повторная попытка авторизации
            result = self.login(username, password, None, auth_code, two_factor_code)

        return result


if __name__ == "__main__":
    # создаем экземпляр класса для авторизации
    client = SteamLogin()

    # начало работы
    LOG.info("Начало работы модуля авторизации")
    LOG.info("-"*30)

    try:
        # пытаемся поднять сессию из сохраненных данных если они в наличии
        LOG.info("Попытка подключения к созданной сессии")
        session = requests.Session()
        with open("secrets/lastlogin.txt", 'r') as lastuser:
            client.username = lastuser.read()
            LOG.debug(client.username)
            LOG.info("-"*30)
        with open(f'secrets/{client.username}.txt', 'rb') as cookiejar:
            session.cookies.update(pickle.load(cookiejar))
            LOG.debug(session.cookies)
            LOG.info("-"*30)
    except Exception as err:
        LOG.info(err)
        # если сессия еще не создавалась или истекли cookies
        LOG.info("Предыдущая сессия не валидна. Требуется авторизация")
        # попытка авторизации
        result = client.cli_login()
        # создаем requests.session()
        session = client.get_web_session()
        with open("secrets/lastlogin.txt", 'w') as userdump:
            userdump.write(client.username)
        with open(f'secrets/{client.username}.txt', 'wb') as cookiejar:
            session_id = generate_session_id()
            for domain in ['store.steampowered.com', 'help.steampowered.com', 'steamcommunity.com']:
                session.cookies.set('sessionid', session_id, domain=domain)
            LOG.info(session.cookies)
            pickle.dump(session.cookies, cookiejar)
        LOG.info("-"*30)

        # если авторизация не удалась по неизвестной ошибке - выводим ошибку в лог
        if result != EResult.OK:
            LOG.info("Failed to login: %s" % repr(result))
            raise SystemExit


# пытаемся забрать информацию с сайта используя текущую сессию
try:
    page = session.get("https://store.steampowered.com/account/history/")
    html_text = page.text
    account = re.search(r'<title>(?P<account>.*?)\'.*</title>', html_text).group('account')
    nickname = re.search(r'submenu_username">\s*(?P<nickname>.*?)\s*</a>', html_text).group('nickname')
    balance = re.search(r'store_transactions/">(?P<balance>.*?)</a>', html_text).group('balance')
    avatar = re.search(r'<a\shref="https://steamcommunity.com/id/.*/">\s*<img\s*src="(?P<avatar>.*?)\s', html_text).group('avatar')
    LOG.info("Аккаунт %s", account)
    LOG.info("Псевдоним: %s", nickname)
    LOG.info("Аватар: %s", avatar)
    LOG.info("Баланс кошелька: %s", balance)
except Exception as err:
    LOG.debug(str(err))
    LOG.info("Houston, we have a problem")
