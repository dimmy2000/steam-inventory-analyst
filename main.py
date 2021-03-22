"""DOCSTRING."""
import json
import logging

from auth import SteamLogin

from webapp.database import create_user

from steam.enums import ECurrencyCode, EResult
from steam.enums.emsg import EMsg


# Настройка логирования
logging.basicConfig(filename='steam_stat.log',
                    filemode='w',
                    encoding='utf-8',
                    format="%(asctime)s | %(levelname)s | %(message)s",
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level=logging.INFO)
LOG = logging.getLogger()


# Создаем экземпляр класса для авторизации
client = SteamLogin()
balance = 0
currency = ''


@client.on("error")
def handle_error(result_):
    """Ловим ошибку авторизации."""
    LOG.info("Результат авторизации: %s", repr(result_))


@client.on("logged_on")
def handle_after_logon():
    """Обрабатываем успешную авторизацию."""
    LOG.info("-" * 57)
    LOG.info("Logged on as: %s", client.user.name)
    LOG.info("Community profile: %s", client.steam_id.community_url)
    LOG.info("Last logon: %s", client.user.last_logon)
    LOG.info("Last logoff: %s", client.user.last_logoff)
    LOG.info("-" * 57)


@client.on("new_login_key")
def store_login_key():
    """Обрабатываем получение токена сессии."""
    LOG.debug("-" * 57)
    LOG.debug("Login key is: %s", client.login_key)
    with open(client.cookies_location, 'r', encoding='utf-8') \
            as cookie_jar:
        cookie = json.load(cookie_jar)
    # Записываем полученный токен в json
    cookie['login_key'] = client.login_key
    with open(client.cookies_location, 'w', encoding='utf-8') \
            as cookie_jar:
        json.dump(cookie, cookie_jar, indent=4)
    LOG.debug("Stored login key is: %s", cookie['login_key'])


@client.on(EMsg.ClientWalletInfoUpdate)
def get_wallet_balance(msg):
    """Сохраняем баланс кошелька в копейках и код используемой валюты."""
    global balance, currency
    balance = msg.body.balance64
    currency = ECurrencyCode(msg.body.currency).name


# Начало работы
LOG.info("Начало работы модуля авторизации")
LOG.info("-" * 57)

result = client.cli_login()

# Создаем requests.Session()
session = client.get_web_session()

# Пытаемся забрать информацию с сайта используя текущую сессию
try:

    # Пытаемся получить логин аккаунта
    account = client.username
    LOG.info("Аккаунт: %s", account)

    try:
        # Пытаемся получить игровой псевдоним пользователя
        nickname = client.user.name
        LOG.info("Псевдоним: %s", nickname)
    except (TypeError, ValueError) as err:
        LOG.info(err)
        LOG.info("Get nickname failed")

    LOG.info("-" * 57)

    avatar = client.user.get_avatar_url(1)
    steam_id = int(client.steam_id)

    create_user(steam_id, account, avatar, balance, currency)

except Exception as err:
    LOG.info(type(err))
    LOG.info(err)
    LOG.info("Houston, we have a problem")

# если авторизация не удалась - выводим ошибку в лог
if result != EResult.OK:
    LOG.info("Failed to login: %s" % repr(result))
    raise SystemExit
