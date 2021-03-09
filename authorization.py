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

    # метод из базового класса SteamClient
    def cli_login(self, username='', password=''):
        """Generates CLI prompts to complete the login process

        :param username: optionally provide username
        :type  username: :class:`str`
        :param password: optionally provide password
        :type  password: :class:`str`
        :return: logon result, see `CMsgClientLogonResponse.eresult <https://github.com/ValvePython/steam/blob/513c68ca081dc9409df932ad86c66100164380a6/protobufs/steammessages_clientserver.proto#L95-L118>`_
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
            username = _cli_input("Username: ")
        if not password:
            password = getpass()

        auth_code = two_factor_code = None
        prompt_for_unavailable = True

        result = self.login(username, password)

        while result in (EResult.AccountLogonDenied, EResult.InvalidLoginAuthCode,
                         EResult.AccountLoginDeniedNeedTwoFactor, EResult.TwoFactorCodeMismatch,
                         EResult.TryAnotherCM, EResult.ServiceUnavailable,
                         EResult.InvalidPassword,
                         ):
            self.sleep(0.1)

            if result == EResult.InvalidPassword:
                password = getpass("Invalid password for %s. Enter password: " % repr(username))

            elif result in (EResult.AccountLogonDenied, EResult.InvalidLoginAuthCode):
                prompt = ("Enter email code: " if result == EResult.AccountLogonDenied else
                          "Incorrect code. Enter email code: ")
                auth_code, two_factor_code = _cli_input(prompt), None

            elif result in (EResult.AccountLoginDeniedNeedTwoFactor, EResult.TwoFactorCodeMismatch):
                prompt = ("Enter 2FA code: " if result == EResult.AccountLoginDeniedNeedTwoFactor else
                          "Incorrect code. Enter 2FA code: ")
                auth_code, two_factor_code = None, _cli_input(prompt)

            elif result in (EResult.TryAnotherCM, EResult.ServiceUnavailable):
                if prompt_for_unavailable and result == EResult.ServiceUnavailable:
                    while True:
                        answer = _cli_input("Steam is down. Keep retrying? [y/n]: ").lower()
                        if answer in 'yn': break

                    prompt_for_unavailable = False
                    if answer == 'n': break

                self.reconnect(maxdelay=15)  # implements reconnect throttling

            result = self.login(username, password, None, auth_code, two_factor_code)

        return result

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
