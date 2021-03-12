"""
ЗДЕСЬ МОГЛА БЫТЬ РЕКЛАМА
но весь маркетинговый бюджет ушел на булочку с корицей :<
"""

import logging
import json
import os
import re

from getpass import getpass
from steam.client import SteamClient
from steam.enums import EResult
from steam.enums.emsg import EMsg
from steam.utils.web import generate_session_id

# настройка логирования
logging.basicConfig(format="%(asctime)s | %(message)s",
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=logging.INFO)
LOG = logging.getLogger()


# переопределяем базовый класс SteamClient
class SteamLogin(SteamClient):
    '''
    Создает экземпляр класса SteamClient, который позволяет получать
    информацию о пользователе, приложениях и предметах на площадках Steam
    через Steam API или OpenID, а также создавать веб-сессию и передавать
    ее как сущность requests.Session() для запросов на сайты:
    steamcommunity.com
    help.steampowered.com
    store.steampowered.com
    '''

    # указываем путь к папке для хранения персональной информации
    credential_location = "secrets"

    # указываем путь к файлу для хранения последней сессии
    cookies_location = os.path.join(credential_location, 'lastlogin.json')

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

        Example console output after calling :meth:`cli_login`

        .. code:: python

            In [5]: client.cli_login()
            Steam username: myusername
            Password:
            Steam is down. Keep retrying? [y/n]: y
            Invalid password for 'myusername'. Enter password:
            Enter email code: 123
            Incorrect code. Enter email code: K6VKF
            Out[5]: <EResult.OK: 1>
        """
        if not username:
            # если файл lastlogin.json создан, считываем из него данные для авторизации
            if os.path.exists(self.cookies_location):
                with open(self.cookies_location, 'r', encoding='utf-8') as cookie_jar:
                    credentials = json.load(cookie_jar)
                username = credentials['username']
                login_key = credentials['login_key']
            else:
                username = input("Имя аккаунта Steam: ")
                login_key = None
        # в противном случае запрашиваем имя, пароль и код 2FA
        if not login_key:
            if not password:
                # если из lastlogin.json не был загружен login_key, проводим стандартную авторизацию
                    password = getpass(prompt="Пароль: ")
            if not two_factor_code:
                    two_factor_code = input("Введите код из мобильного приложения Steam: ")

        auth_code = None
        prompt_for_unavailable = True

        credentials = {
                'username': username,
                'login_key': login_key,
        }

        if login_key:
            # попытка авторизации из сохраненной сессии
            result = self.login(username,
                                '',
                                login_key)
        else:
            # попытка авторизации с введенными пользовательскими данными
            result = self.login(username, password, login_key, auth_code, two_factor_code)

        # ловим ошибки
        while result in (EResult.AccountLogonDenied,
                         EResult.InvalidLoginAuthCode,
                         EResult.AccountLoginDeniedNeedTwoFactor,
                         EResult.TwoFactorCodeMismatch,
                         EResult.TryAnotherCM,
                         EResult.ServiceUnavailable,
                         EResult.InvalidPassword,
                         ):
            self.sleep(0.1)

            # введен направильный пароль
            if result == EResult.InvalidPassword:
                password = getpass("Пароль для %s введен неверно. "
                                   "Введите пароль: " % repr(username))

            # требуется код из е-мэйла
            elif result in (EResult.AccountLogonDenied,
                            EResult.InvalidLoginAuthCode):
                prompt = ("Введите код, высланный на ваш e-mail: "
                          if result == EResult.AccountLogonDenied
                          else "Код введен неверно. "
                               "Введите код, высланный на ваш e-mail: ")
                auth_code, two_factor_code = input(prompt), None

            # требуется код из мобильного приложения
            elif result in (EResult.AccountLoginDeniedNeedTwoFactor,
                            EResult.TwoFactorCodeMismatch):
                prompt = ("Введите код из мобильного приложения: "
                          if result == EResult.AccountLoginDeniedNeedTwoFactor
                          else "Код введен неверно... Попробуйте еще раз: ")
                auth_code, two_factor_code = None, input(prompt)

            # сервис недоступен
            elif result in (EResult.TryAnotherCM,
                            EResult.ServiceUnavailable):
                if prompt_for_unavailable and result == EResult.ServiceUnavailable:
                    while True:
                        answer = input("Steam недоступен. "
                                       "Повторить попытку подключения? [y/n]: ").lower()
                        if answer in 'yn':
                            break

                    prompt_for_unavailable = False
                    if answer == 'n':
                        break

                # устанавливаем задержку для переподключения
                self.reconnect(maxdelay=15)

            # повторная попытка авторизации
            result = self.login(username,
                                password,
                                None,
                                auth_code,
                                two_factor_code)

        # записываем данные для восстановления сессии в json
        with open(self.cookies_location, 'w', encoding='utf-8') as cookie_jar:
            json.dump(credentials, cookie_jar, indent=4)

        return result


if __name__ == "__main__":
    # создаем экземпляр класса для авторизации
    client = SteamLogin()

    # хандлеры для обработки состояний

    # ловим ошибку авторизации
    @client.on("error")
    def handle_error(result):
        LOG.info("Результат авторизации: %s", repr(result))

    # обрабатываем событие канал зашифрован
    @client.on("channel_secured")
    def send_login():
        if client.relogin_available:
            client.relogin()

    # обрабатываем подключение к серверу
    @client.on("connected")
    def handle_connected():
        LOG.info("Подключен к %s", client.current_server_addr)

    # обрабатываем попытку переподключения
    @client.on("reconnect")
    def handle_reconnect(delay):
        LOG.info("Переподключение через %ds...", delay)

    # обрабатываем отключение от сервера
    @client.on("disconnected")
    def handle_disconnect():
        LOG.info("Соединение разорвано.")

        if client.relogin_available:
            LOG.info("Переподключение...")
            client.reconnect(maxdelay=30)

    # обрабатываем успешную авторизацию
    @client.on("logged_on")
    def handle_after_logon():
        LOG.info("-"*30)
        LOG.info("Logged on as: %s", client.user.name)
        LOG.info("Community profile: %s", client.steam_id.community_url)
        LOG.info("Last logon: %s", client.user.last_logon)
        LOG.info("Last logoff: %s", client.user.last_logoff)
        LOG.info("-"*30)
        LOG.info("Press ^C to exit")
        LOG.info("-" * 30)

    # обрабатываем получение токена сессии
    @client.on("new_login_key")
    def store_login_key():
        LOG.debug("-" * 30)
        LOG.debug("Login key is: %s", client.login_key)
        with open(client.cookies_location, 'r', encoding='utf-8') as cookie_jar:
            cookie = json.load(cookie_jar)
        # записываем полученный токен в json
        cookie['login_key'] = client.login_key
        with open(client.cookies_location, 'w', encoding='utf-8') as cookie_jar:
            json.dump(cookie, cookie_jar)
        LOG.debug("Stored login key is: %s", cookie['login_key'])


    # начало работы
    LOG.info("Начало работы модуля авторизации")
    LOG.info("-" * 30)

    try:
        LOG.info("Начинаем авторизацию")
        LOG.info("-" * 30)
        result = client.cli_login()

        # создаем requests.session()
        session = client.get_web_session()

        # пытаемся забрать информацию с сайта используя текущую сессию
        try:
            page = session.get("https://store.steampowered.com/account/history/")
            html_text = page.text

            with open(f'{client.username}.html', 'w', encoding='utf-8') as f:
                f.write(html_text)
            try:
                # пытаемся получить логин аккаунта
                account = re.search(r'<title>(?P<account>.*?)\'.*</title>', html_text).group('account')
                LOG.info("Аккаунт %s", account)
            except Exception as err:
                LOG.info(err)
                LOG.info("Get account failed")
            try:
                # пытаемся получить игровой псевдоним пользователя
                nickname = re.search(r'submenu_username">\s*(?P<nickname>.*?)\s*</a>', html_text).group('nickname')
                LOG.info("Псевдоним: %s", nickname)
            except Exception as err:
                LOG.info(err)
                LOG.info("Get nickname failed")
            try:
                # пытаемся получить данные о балансе кошелька
                balance = re.search(r'store_transactions/">(?P<balance>.*?)</a>', html_text).group('balance')
                LOG.info("Баланс кошелька: %s", balance)
            except Exception as err:
                LOG.info(err)
                LOG.info("Get balance failed")
            try:
                # пытаемся получить ссылку на аватар пользователя
                avatar = re.search(r'class="user_avatar\s*playerAvatar\s*online">\s*<img\s*src="(?P<avatar>.*?)"',
                                   html_text).group('avatar')
                LOG.info("Аватар: %s", avatar)
            except Exception as err:
                LOG.info(err)
                LOG.info("Get avatar failed")

            LOG.info("-" * 30)

        except Exception as err:
            LOG.debug(str(err))
            LOG.info("Houston, we have a problem")

        # если авторизация не удалась по неизвестной ошибке - выводим ошибку в лог
        if result != EResult.OK:
            LOG.info("Failed to login: %s" % repr(result))
            raise SystemExit

        # запускаем бесконечный цикл
        client.run_forever()

    except KeyboardInterrupt:
        if client.connected:
            LOG.info("Logout")
            client.logout()