# -*- coding: utf-8 -*-
from datetime import datetime

from config import Config

from webapp.database.models import User, db

from flask import Flask, flash, redirect, render_template, request, url_for

from flask_login import LoginManager, current_user, login_required, \
    login_user, logout_user

from webapp.forms import LoginForm, RegistrationForm

from werkzeug.urls import url_parse


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    @app.route('/index')
    @login_required
    def index():
        title = 'Home'
        posts = [
            {
                'author': {'username': 'John'},
                'body': 'Beautiful day in Portland!',
            },
            {
                'author': {'username': 'Susan'},
                'body': 'The Avengers movie was so cool!',
            },
            {
                'author': {'username': 'Ипполит'},
                'body': 'Какая гадость эта ваша заливная рыба!!',
            },
        ]
        return render_template('index.html', title=title, posts=posts)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        title = 'Sign In'
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        return render_template('user/login.html', title=title, form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        return render_template('user/register.html', title='Register', form=form)

    @app.route('/profile/<username>')
    @login_required
    def user(username):
        user = User.query.filter_by(username=username).first_or_404()
        posts = [
                {'owner': user, 'body': 'susan #1'},
                {'owner': user, 'body': 'strong #2'},
                ]
        return render_template('user/profile.html', user=user, posts=posts)

    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()


    return app
