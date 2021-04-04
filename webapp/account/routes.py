"""Реализация разделов сайта для работы с аккаунтами Steam."""
import os

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from webapp import db, get_logger
from webapp.account.forms import SteamLoginForm
from webapp.account.models import Account
from webapp.account.utils import auth_attempt, update_acc_info
from webapp.user.models import User

blueprint = Blueprint('account', __name__,
                      url_prefix='/accounts')
logger = get_logger('account.routes')


@blueprint.route('/make_session', methods=['GET', 'POST'])
@login_required
def make_session():
    """Подключение для пользователя нового аккаунта Steam."""
    title = 'Подключение аккаунта Steam'
    form = SteamLoginForm()
    user = db.session.query(User).filter_by(
        username=current_user.username).first()
    accounts = db.session.query(Account).filter_by(
        user_id=user.user_id).all()

    auth_code = None
    two_factor_code = None

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if form.auth_code.data:
            auth_code = form.auth_code.data
        if form.two_factor_code.data:
            two_factor_code = form.two_factor_code.data

        try_login = auth_attempt(user=user, username=username,
                                 password=password, auth_code=auth_code,
                                 two_factor_code=two_factor_code)
        if try_login:
            return redirect(url_for('user.profile',
                                    username=current_user.username))
        else:
            flash('Неудачная попытка авторизации', 'warning')

    template_path = os.path.join('account', 'make_session.html')
    return render_template(template_path,
                           title=title,
                           form=form,
                           user=user,
                           accounts=accounts)


@blueprint.route('/<steam_login>')
def account(steam_login):
    """Информация о подключенном аккаунте Steam."""
    title = f'Аккаунт {steam_login}'

    user = db.session.query(User).filter_by(
        username=current_user.username).first()

    steam_acc = db.session.query(Account).filter_by(
        user_id=user.user_id,
        username=steam_login).first()

    if steam_acc:
        update_acc_info(steam_acc)

    template_path = os.path.join('account', 'account.html')
    return render_template(template_path, title=title, user=user)


@blueprint.route('/<steam_login>/trade_history')
def trade_history(steam_login):
    """Информация об истории торговли подключенного аккаунта Steam."""
    title = f'История торговли {steam_login}'
    template_path = os.path.join('account', 'trade_history.html')
    return render_template(template_path, title=title)


@blueprint.route('/<steam_login>/items/<item_id>')
def item_description(steam_login, item_id):
    """Описание предмета из коллекции Steam."""
    title = 'title'
    template_path = os.path.join('account', 'item.html')
    return render_template(template_path, title=title)
