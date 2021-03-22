from flask import Blueprint, flash, redirect, render_template, request, url_for

from flask_login import current_user, login_required, login_user, logout_user

from webapp import User, db
from webapp.user.forms import LoginForm, RegistrationForm

from werkzeug.urls import url_parse

blueprint = Blueprint('user', __name__, url_prefix='/users')


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    title = 'Авторизация'
    if current_user.is_authenticated:
        return redirect(url_for('user.profile',
                                username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('user.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('user.profile', username=form.username.data)
        return redirect(next_page)
    return render_template('user/login.html', title=title, form=form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('user.login'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    title = 'Регистрация'
    if current_user.is_authenticated:
        return redirect(url_for('user.login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('user.login'))
    return render_template('user/register.html', title=title,
                           form=form)


@blueprint.route('/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'owner': user, 'body': 'susan #1'},
        {'owner': user, 'body': 'strong #2'},
    ]
    return render_template('user/profile.html', user=user, posts=posts)
