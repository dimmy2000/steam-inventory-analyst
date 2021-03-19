"""ЗДЕСЬ МОГЛА БЫТЬ РЕКЛАМА.

но весь маркетинговый бюджет ушел на булочку с корицей :<

SteamLogin - Создает экземпляр класса SteamClient из библиотеки steam,
который позволяет получать информацию о пользователе, приложениях и предметах
на площадках Steam через Steam API или OpenID, а также создавать веб-сессию и
передавать ее как сущность requests.Session() для запросов на сайты:
steamcommunity.com, help.steampowered.com и store.steampowered.com
"""

import json
import os
from getpass import getpass

from steam.client import SteamClient
from steam.enums import EResult


class SteamLogin(SteamClient):
    """Создает экземпляр класса SteamClient.

    У пользователя запрашивается логин, пароль, токен из мобильного приложения
    Steam, которые используются для попытки авторизации на сервисах Steam.
    В случае неудачи, поднимается исключение и выводится запрос на ввод
    недостающих данных, либо сведения об ошибке.

    В процессе авторизации создается папка 'secrets' для хранения секретных
    ключей. В нее заносятся необходимые данные о пользователе для
    восстановления сессии без повторной авторизации.

    Если в папке'secrets' имеются необходимые данные, производится попытка
    восстановления сессии. В случае неудачи, у пользователя запрашиваются
    данные для авторизации.

    """

    # Указываем путь к папке для хранения персональной информации
    credential_location = "secrets"
    # Указываем путь к файлу для хранения последней сессии
    cookies_location = os.path.join(credential_location, 'lastlogin.json')

    # Переопределяем метод из базового класса SteamClient
    def cli_login(self, username='', password='', two_factor_code=None):
        """Выводит в консоль необходимые запросы для совершения авторизации.

        :param username: при необходимости передаем имя пользователя
        :type  username: :class:`str`
        :param password: при необходимости передаем пароль
        :type  password: :class:`str`
        :param two_factor_code: при необходимости передаем код из
        мобильного приложения
        :type  two_factor_code: :class:`str`
        :return: logon result, see `CMsgClientLogonResponse.eresult
        :rtype: :class:`.EResult`

        Example console output after calling :meth:`cli_login`

        .. code:: python

            In [5]: client.cli_login()
            Имя аккаунта Steam: myusername
            Пароль:
            Введите код из мобильного приложения Steam: DD5X4
            Steam недоступен. Повторить попытку подключения? [y/n]: y
            Пароль для 'myusername' введен неверно. Введите пароль:
            Enter email code: 123
            Incorrect code. Enter email code: K6VKF
            Out[5]: <EResult.OK: 1>
        """
        if not username:
            # Если создан lastlogin.json берем из него данные для авторизации
            if os.path.exists(self.cookies_location):
                with open(self.cookies_location, 'r',
                          encoding='utf-8') as cookie_jar:
                    credentials = json.load(cookie_jar)

                username = credentials['username']
                login_key = credentials['login_key']
            else:
                username = input("Имя аккаунта Steam: ")
                login_key = None

        # В противном случае запрашиваем имя, пароль и код 2FA
        if not login_key:
            if not password:
                # Если не создан login_key, проводим стандартную авторизацию
                password = getpass(prompt="Пароль: ")
            if not two_factor_code:
                two_factor_code = input("Введите код из мобильного приложения"
                                        " Steam: ")

        auth_code = None
        prompt_for_unavailable = True

        credentials = {'username': username,
                       'login_key': login_key}

        if login_key:
            # Попытка авторизации из сохраненной сессии
            result = self.login(username,
                                '',
                                login_key)
        else:
            # Попытка авторизации с введенными пользовательскими данными
            result = self.login(username, password, login_key, auth_code,
                                two_factor_code)

        # Ловим ошибки
        while result in (EResult.AccountLogonDenied,
                         EResult.InvalidLoginAuthCode,
                         EResult.AccountLoginDeniedNeedTwoFactor,
                         EResult.TwoFactorCodeMismatch,
                         EResult.TryAnotherCM,
                         EResult.ServiceUnavailable,
                         EResult.InvalidPassword):
            self.sleep(0.1)

            # Введен направильный пароль
            if result == EResult.InvalidPassword:
                login_key = None

                credentials = {'username': username,
                               'login_key': login_key}

                with open(self.cookies_location, 'w',
                          encoding='utf-8') as cookie_jar:
                    json.dump(credentials, cookie_jar, indent=2)

                password = getpass("Пароль для %s введен неверно. "
                                   "Введите пароль: " % repr(username))

            # Требуется код из е-мэйла
            elif result in (EResult.AccountLogonDenied,
                            EResult.InvalidLoginAuthCode):
                prompt = ("Введите код, высланный на ваш e-mail: "
                          if result == EResult.AccountLogonDenied
                          else "Код введен неверно. "
                               "Введите код, высланный на ваш e-mail: ")
                auth_code, two_factor_code = input(prompt), None

            # Требуется код из мобильного приложения
            elif result in (EResult.AccountLoginDeniedNeedTwoFactor,
                            EResult.TwoFactorCodeMismatch):
                prompt = ("Введите код из мобильного приложения: "
                          if result == EResult.AccountLoginDeniedNeedTwoFactor
                          else "Код введен неверно... Попробуйте еще раз: ")
                auth_code, two_factor_code = None, input(prompt)

            # Сервис недоступен
            elif result in (EResult.TryAnotherCM,
                            EResult.ServiceUnavailable):
                if prompt_for_unavailable and \
                        result == EResult.ServiceUnavailable:
                    while True:
                        answer = input("Steam недоступен. "
                                       "Повторить попытку подключения? "
                                       "[y/n]: ").lower()
                        if answer in 'yn':
                            break

                    prompt_for_unavailable = False
                    if answer == 'n':
                        break

                # Устанавливаем задержку для переподключения
                self.reconnect(maxdelay=15)

            # Повторная попытка авторизации
            result = self.login(username,
                                password,
                                None,
                                auth_code,
                                two_factor_code)

        # Если отсутствует папка для хранения секретов - создаем ее
        if not os.path.exists(self.credential_location):
            os.makedirs(self.credential_location)
        # Записываем данные для восстановления сессии в json
        with open(self.cookies_location, 'w', encoding='utf-8') as cookie_jar:
            json.dump(credentials, cookie_jar, indent=2)

        return result
