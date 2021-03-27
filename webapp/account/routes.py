"""Реализация разделов сайта для работы с Steam-воркерами."""
from flask import Blueprint, flash, redirect, render_template, url_for

from flask_login import current_user, login_required

from steam.client import SteamClient
from steam.enums import ECurrencyCode, EResult
from steam.enums.emsg import EMsg

from webapp import User, Account, db
from webapp.account.forms import SteamLoginForm

blueprint = Blueprint('account', __name__,
                      url_prefix='/accounts')


@blueprint.route('/get_session', methods=['GET', 'POST'])
@login_required
def get_session():
    """Авторизация воркера на серверах Steam."""
    title = 'Подключение воркера'
    form = SteamLoginForm()

    client = SteamClient()

    login_key = None
    auth_code = None
    two_factor_code = None
    balance = 0
    currency = ''

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if form.auth_code.data:
            auth_code = form.auth_code.data
        if form.two_factor_code.data:
            two_factor_code = form.two_factor_code.data

        try:
            result = client.login(username, password, login_key, auth_code,
                                  two_factor_code)

            @client.on("new_login_key")
            def fetch_login_key():
                """Обрабатываем получение токена сессии."""
                print(f"Login key is: {client.login_key}", 'info')
                nonlocal login_key
                login_key = client.login_key

            @client.on(EMsg.ClientWalletInfoUpdate)
            def get_wallet_balance(msg):
                """Получаем данные по кошельку.

                Сохраняем баланс кошелька в копейках и код используемой
                валюты.
                """
                nonlocal balance, currency
                balance = msg.body.balance64
                currency = ECurrencyCode(msg.body.currency).name
                print(f"Balance is: {balance} {currency}", 'info')

            if result == EResult.OK:
                user = User.query.filter_by(
                    username=current_user.username).first()
                steam_id = int(client.steam_id)
                avatar = client.user.get_avatar_url(2)
                worker = Account(steam_id=steam_id,
                                 username=username,
                                 login_key=login_key,
                                 avatar_url=avatar,
                                 wallet_balance=balance,
                                 currency=currency,
                                 user_id=int(user.user_id))
                flash(f'Logged as {username}, profile {steam_id}\n'
                      f'Balance: {balance} {currency}', 'info')
                print(worker)
                try:
                    db.session.add(worker)
                    db.session.commit()
                except Exception as e:
                    flash(e, 'info')
                    print(e)
                return redirect(url_for('user.profile',
                                        username=current_user.username))

            elif result == EResult.InvalidPassword:
                flash('Invalid password', 'EResult')
                print('Invalid password', 'EResult')

            elif result in (EResult.AccountLogonDenied,
                            EResult.InvalidLoginAuthCode):
                flash("Enter email code", 'EResult')
                print("Enter email code", 'EResult')

            elif result in (EResult.AccountLoginDeniedNeedTwoFactor,
                            EResult.TwoFactorCodeMismatch):
                flash('Enter 2FA-code', 'EResult')
                print('Enter 2FA-code', 'EResult')

        except Exception as e:
            flash(e, 'info')
            print(e)

    return render_template('account/create_session.html', title=title, form=form)
