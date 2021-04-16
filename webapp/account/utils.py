"""Внешние утилиты для работы с подключенными аккаунтами."""
from flask import current_app, flash, redirect, url_for
from steam.enums import EResult

from tasks import save_acc_info
from webapp.extensions.steam_client import SteamLogin


def auth_attempt(
        user_id,
        username,
        password,
        auth_code=None,
        two_factor_code=None,
):
    """Авторизация на серверах Steam.

    По полученным учетным данным делаем попытку авторизации с помощью
    SteamClient(). При успешном входе пишем полученные данные о пользователе
    в БД с помощью таска селери save_acc_info и возвращаем True. В случае
    неудачной авторизации обрабатываем возможные запросы ввода дополнительных
    данных. В случае невозможности устранения причин отказа в авторизации
    возвращаем False.
    """
    current_app.logger.info("Auth attempt function")
    client = SteamLogin()

    login_result = client.login(
        username=username,
        password=password,
        auth_code=auth_code,
        two_factor_code=two_factor_code,
    )

    # Выводим сообщение с результатом авторизации в лог
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

        client.logout()

        save_acc_info.delay(
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
        return True

    elif login_result == EResult.InvalidPassword:
        flash('Invalid password', 'EResult')
        current_app.logger.info('Invalid password')
        return url_for('account.make_session', login=username)

    elif login_result in (EResult.AccountLogonDenied,
                          EResult.InvalidLoginAuthCode):
        flash("Enter email code", 'EResult')
        current_app.logger.info("Enter email code")
        return url_for('account.make_session', login=username)

    elif login_result in (EResult.AccountLoginDeniedNeedTwoFactor,
                          EResult.TwoFactorCodeMismatch):
        flash('Enter 2FA-code', 'EResult')
        current_app.logger.info('Enter 2FA-code')
        return url_for('account.make_session', login=username)

    return False



