import json
import logging
import re

from steam.enums import EResult

from auth import SteamLogin

# настройка логирования
logging.basicConfig(format="%(asctime)s | %(message)s",
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=logging.INFO)
LOG = logging.getLogger()


if __name__ == "__main__":
    # создаем экземпляр класса для авторизации
    client = SteamLogin()

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
        LOG.info("-" * 30)
        LOG.info("Logged on as: %s", client.user.name)
        LOG.info("Community profile: %s", client.steam_id.community_url)
        LOG.info("Last logon: %s", client.user.last_logon)
        LOG.info("Last logoff: %s", client.user.last_logoff)
        LOG.info("-" * 30)
        LOG.info("Press ^C to exit")
        LOG.info("-" * 30)

    # обрабатываем получение токена сессии
    @client.on("new_login_key")
    def store_login_key():
        LOG.debug("-" * 30)
        LOG.debug("Login key is: %s", client.login_key)
        with open(client.cookies_location, 'r', encoding='utf-8') \
                as cookie_jar:
            cookie = json.load(cookie_jar)
        # записываем полученный токен в json
        cookie['login_key'] = client.login_key
        with open(client.cookies_location, 'w', encoding='utf-8') \
                as cookie_jar:
            json.dump(cookie, cookie_jar, indent=4)
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
            page = session.get("https://store.steampowered.com/account/"
                               "history/")
            html_text = page.text

            try:
                # пытаемся получить логин аккаунта
                account = re.search(r'<title>(?P<account>.*?)\'.*</title>',
                                    html_text).group('account')
                LOG.info("Аккаунт %s", account)
            except AttributeError as err:
                LOG.info(err)
                LOG.info("Get account failed")
            try:
                # пытаемся получить игровой псевдоним пользователя
                nickname = re.search(r'submenu_username">\s*(?P<nickname>.*?)'
                                     r'\s*</a>', html_text).group('nickname')
                LOG.info("Псевдоним: %s", nickname)
            except AttributeError as err:
                LOG.info(err)
                LOG.info("Get nickname failed")
            try:
                # пытаемся получить данные о балансе кошелька
                balance = re.search(r'store_transactions/">(?P<balance>.*?)'
                                    r'</a>', html_text).group('balance')
                LOG.info("Баланс кошелька: %s", balance)
            except AttributeError as err:
                LOG.info(err)
                LOG.info("Get balance failed")
            try:
                # пытаемся получить ссылку на аватар пользователя
                avatar = re.search(r'class="user_avatar\s*playerAvatar\s*'
                                   r'online">\s*<img\s*src="(?P<avatar>.*?)"',
                                   html_text).group('avatar')
                LOG.info("Аватар: %s", avatar)
            except AttributeError as err:
                LOG.info(err)
                LOG.info("Get avatar failed")

            LOG.info("-" * 30)

        except Exception as err:
            LOG.info(type(err))
            LOG.info(str(err))
            LOG.info("Houston, we have a problem")

        # если авторизация не удалась - выводим ошибку в лог
        if result != EResult.OK:
            LOG.info("Failed to login: %s" % repr(result))
            raise SystemExit

        # запускаем бесконечный цикл
        client.run_forever()

    except KeyboardInterrupt:
        if client.connected:
            LOG.info("Logout")
            client.logout()
