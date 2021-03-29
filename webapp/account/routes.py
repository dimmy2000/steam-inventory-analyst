"""Реализация разделов сайта для работы с Steam-воркерами."""
from flask import Blueprint, flash, redirect, render_template, url_for
import logging
import os

from flask_login import current_user, login_required

from steam.client import SteamClient, EMsg
from steam.enums import ECurrencyCode, EResult

from webapp import User, Account, db
from webapp.account.forms import SteamLoginForm
from webapp.account.utils import save_acc_info

blueprint = Blueprint('account', __name__,
                      url_prefix='/accounts')


@blueprint.route('/get_session', methods=['GET', 'POST'])
@login_required
def get_session():
    """Авторизация на серверах Steam."""
    title = 'Подключение воркера'
    form = SteamLoginForm()

    client = SteamClient()

    auth_code = None
    two_factor_code = None

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if form.auth_code.data:
            auth_code = form.auth_code.data
        if form.two_factor_code.data:
            two_factor_code = form.two_factor_code.data

        try:
            result = client.login(username,
                                  password,
                                  None,
                                  auth_code,
                                  two_factor_code)
            logging.info(f"Login result: {result}")

            if result == EResult.OK:
                user = User.query.filter_by(username=current_user.username).first()
                logging.info(f"Got: {user}")
                flash(f'Logged on as {username}', 'info')
                logging.info(f'Logged on as {username}')
                steam_id = int(client.steam_id)
                avatar = client.user.get_avatar_url(2)
                login_key = client.login_key
                steam_acc = Account(steam_id=steam_id,
                                    username=username,
                                    login_key=login_key,
                                    avatar_url=avatar,
                                    user_id=int(user.user_id))
                try:
                    db.session.add(steam_acc)
                    db.session.commit()
                    logging.info("Successful db insert")
                except Exception as e:
                    flash(e, 'info')
                    logging.info(e)
                return redirect(url_for('user.profile',
                                        username=current_user.username))

            elif result == EResult.InvalidPassword:
                flash('Invalid password', 'EResult')
                logging.info('Invalid password')

            elif result in (EResult.AccountLogonDenied,
                            EResult.InvalidLoginAuthCode):
                flash("Enter email code", 'EResult')
                logging.info("Enter email code")

            elif result in (EResult.AccountLoginDeniedNeedTwoFactor,
                            EResult.TwoFactorCodeMismatch):
                flash('Enter 2FA-code', 'EResult')
                logging.info('Enter 2FA-code')

        except Exception as e:
            flash(e, 'info')
            logging.info(e)

    template_path = os.path.join('account', 'create_session.html')
    return render_template(template_path, title=title, form=form)
