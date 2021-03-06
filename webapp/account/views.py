"""Реализация разделов сайта для работы с аккаунтами Steam."""
import os

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from webapp.account.forms import SteamLoginForm
from webapp.account.utils import auth_attempt, load_inventory_contents, \
    update_acc_info, update_inventory_contents
from webapp.db import db
from webapp.user.models import User

blueprint = Blueprint('account', __name__,
                      url_prefix='/accounts')


@blueprint.route('/make_session', methods=['GET', 'POST'])
@login_required
def make_session():
    """Подключение для пользователя нового аккаунта Steam."""
    title = 'Подключение аккаунта Steam'
    form = SteamLoginForm()
    user = User.query.filter_by(username=current_user.username).first()
    accounts = user.accounts.all()

    # Если есть атрибут login - вставляем его в поле username шаблона
    login = request.args.get('login')
    if login is None:
        login = ''

    auth_code = None
    two_factor_code = None

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if form.auth_code.data:
            auth_code = form.auth_code.data
        if form.two_factor_code.data:
            two_factor_code = form.two_factor_code.data
        user_id = user.user_id

        try_login = auth_attempt(
            user_id=user_id,
            username=username,
            password=password,
            auth_code=auth_code,
            two_factor_code=two_factor_code,
        )
        if try_login:
            # Обновляем сессию пользователя после коммита
            user = User.query.filter_by(user_id=user_id).first()
            if type(try_login) == str:
                return redirect(try_login)
            else:
                return redirect(url_for(
                    'user.profile',
                    username=user.username,
                ))
        else:
            flash('Неудачная попытка авторизации', 'warning')

    template_path = os.path.join('account', 'make_session.html')
    return render_template(
        template_path,
        title=title,
        login=login,
        form=form,
        user=user,
        accounts=accounts,
    )


@blueprint.route('/<steam_login>')
@login_required
def account(steam_login):
    """Информация о подключенном аккаунте Steam."""
    title = f'Аккаунт {steam_login}'
    user = User.query.filter_by(username=current_user.username).first()
    db_steam_acc = user.accounts.filter_by(username=steam_login).first()

    if db_steam_acc:
        items = load_inventory_contents(db_steam_acc)
        update_acc_info(db_steam_acc)
        update_inventory_contents(db_steam_acc)
    else:
        items = None

    user = User.query.filter_by(username=current_user.username).first()
    template_path = os.path.join('account', 'account.html')
    return render_template(
        template_path,
        title=title,
        user=user,
        account=db_steam_acc,
        items=items,
    )


@blueprint.route('/<steam_login>/trade_history')
@login_required
def trade_history(steam_login):
    """Информация об истории торговли подключенного аккаунта Steam."""
    title = f'История торговли {steam_login}'
    template_path = os.path.join('account', 'trade_history.html')
    return render_template(
        template_path,
        title=title,
    )


@blueprint.route('/delete/<steam_login>')
@login_required
def remove_account(steam_login):
    """Отключение аккаунта Steam и удаление записи из БД."""
    user = User.query.filter_by(username=current_user.username).first()
    accounts = user.accounts.all()
    fetch_account = user.accounts.filter_by(
        username=steam_login).first_or_404()
    db.session.delete(fetch_account)
    db.session.commit()
    flash(f'Аккаунт {steam_login} отключен.', 'danger')
    template_path = os.path.join('user', 'profile.html')
    return render_template(
        template_path,
        user=user,
        accounts=accounts,
    )
