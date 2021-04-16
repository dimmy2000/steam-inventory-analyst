"""Реализация разделов сайта для работы с пользователями."""
import os

from flask import Blueprint, flash, redirect, render_template, request, url_for

from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from webapp.account.models import Account
from webapp.account.schemas import AccountSchema
from webapp.db import db
from webapp.item.schemas import ItemSchema, DescriptionSchema
from webapp.user.forms import LoginForm, RegistrationForm
from webapp.user.models import User
from webapp.user.schemas import UserSchema

blueprint = Blueprint('user', __name__, url_prefix='/users')


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """Авторизация пользователя."""
    title = 'Авторизация'
    if current_user.is_authenticated:
        return redirect(url_for(
            'user.profile',
            username=current_user.username,
        ))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('user.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('user.profile',
                                username=form.username.data)
        return redirect(next_page)
    template_path = os.path.join('user', 'login.html')
    return render_template(
        template_path,
        title=title,
        form=form,
    )


@blueprint.route('/logout')
def logout():
    """Выход из учетной записи."""
    logout_user()
    return redirect(url_for('user.login'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя."""
    title = 'Регистрация'
    if current_user.is_authenticated:
        return redirect(url_for('user.login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user!', 'success')
        return redirect(url_for('user.login'))
    template_path = os.path.join('user', 'register.html')
    return render_template(
        template_path,
        title=title,
        form=form,
    )


@blueprint.route('/<username>')
@login_required
def profile(username):
    """Профиль зарегистрированного пользователя"""
    user = db.session.query(User).filter_by(username=username).first_or_404()
    accounts = user.accounts.all()
    template_path = os.path.join('user', 'profile.html')
    return render_template(
        template_path,
        user=user,
        accounts=accounts,
    )
