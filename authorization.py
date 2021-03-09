import logging
from steam.client import SteamClient
from steam.enums.emsg import EMsg
from steam.enums import EResult, ECurrencyCode

# настройка логирования
logging.basicConfig(format="%(asctime)s | %(message)s", datefmt='%d-%m-%Y %H:%M:%S', level=logging.INFO)
LOG = logging.getLogger()

# переопределяем базовый класс SteamClient
# TODO: реализовать сбор необходимых для авторизации данных и дамп их на диск
# TODO: реализовать возможность авторизации без ввода данных, если они сохранены на диске
class SteamLogin(SteamClient):
    username = ''
    password = ''
    two_factor_code = ''
    login_key = None

balance = "" # глобальная переменная для хранения информации о балансе кошелька

# создаем экземпляр класса для авторизации
client = SteamLogin()

# указываем путь к папке для хранения персональной информации
client.set_credential_location("secrets")

# хандлеры для обработки состояний
@client.on("error")
def handle_error(result):
    LOG.info("Logon result: %s", repr(result))

@client.on("channel_secured")
def send_login():
    if client.relogin_available:
        client.relogin()

@client.on("connected")
def handle_connected():
    LOG.info("Connected to %s", client.current_server_addr)

@client.on("reconnect")
def handle_reconnect(delay):
    LOG.info("Reconnect in %ds...", delay)

@client.on("disconnected")
def handle_disconnect():
    LOG.info("Disconnected.")

    if client.relogin_available:
        LOG.info("Reconnecting...")
        client.reconnect(maxdelay=30)

# получение данных о состоянии кошелька
@client.on(EMsg.ClientWalletInfoUpdate)
def print_balance(msg):
    bucks, cents = divmod(msg.body.balance64, 100)
    global balance
    balance = "Current balance is {:d}.{:02d} {:s}".format(bucks, cents, ECurrencyCode(msg.body.currency).name)

@client.on("logged_on")
def handle_after_logon():
    LOG.info("-"*30)
    LOG.info("Logged on as: %s", client.user.name)
    LOG.info("Steam profile ID is: %s", client.steam_id)
    LOG.info("Avatar is: %s", client.user.get_avatar_url(0))
    LOG.info(balance)
    LOG.info("Community profile: %s", client.steam_id.community_url)
    LOG.info("Last logon: %s", client.user.last_logon)
    LOG.info("Last logoff: %s", client.user.last_logoff)
    LOG.info("-"*30)
    LOG.info("Press ^C to exit")


# начало работы
LOG.info("Authorization module start")
LOG.info("-"*30)

try:
    result = client.cli_login()

    if result != EResult.OK:
        LOG.info("Failed to login: %s" % repr(result))
        raise SystemExit

    client.run_forever()

except KeyboardInterrupt:
    if client.connected:
        LOG.info("Logout")
        client.logout()
