"""Здесь расположены разделы сайта для работы с воркерами."""
from flask import Blueprint, flash, redirect, render_template, url_for

from flask_login import login_required

from steam.client import SteamClient
from steam.enums import EResult

from webapp.worker.forms import AddWorkerForm

blueprint = Blueprint('worker', __name__,
                      url_prefix='/workers')


@blueprint.route('/add_worker', methods=['GET', 'POST'])
@login_required
def worker_login():
    title = 'Подключение воркера'
    form = AddWorkerForm()

    client = SteamClient()

    login_key = None
    auth_code = None
    two_factor_code = None

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if form.auth_code.data:
            auth_code = form.auth_code.data
        if form.two_factor_code.data:
            two_factor_code = form.two_factor_code.data
        login = f'login({username}, {password}, {login_key}, ' \
                f'{auth_code}, {two_factor_code})'
        flash(login, 'info')
        print(login)
        try:
            result = client.login(username, password, login_key, auth_code,
                                  two_factor_code)

            if result == EResult.OK:
                flash(f'Success {int(client.steam_id)}', 'info')
            elif result == EResult.InvalidPassword:
                flash('Invalid password. Enter password', 'info')

            elif result in (EResult.AccountLogonDenied,
                            EResult.InvalidLoginAuthCode):
                flash("Enter email code", 'info')

            elif result in (EResult.AccountLoginDeniedNeedTwoFactor,
                            EResult.TwoFactorCodeMismatch):
                flash(str(result), 'info')

            else:
                flash(result, 'info')

        except Exception as e:
            flash(e, 'info')
            print(type(e), e)

    return render_template('worker/add_worker.html', title=title, form=form)
