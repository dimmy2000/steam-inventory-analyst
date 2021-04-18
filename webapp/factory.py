"""Основная структура flask-приложения.

Здесь создается экземпляр flask-приложения, сессия для работы с БД,
подключаются расширения для реализации логики.
"""
# -*- coding: utf-8 -*-
import os
from datetime import datetime

from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from flask_migrate import Migrate

from webapp.account.views import blueprint as worker_blueprint
from webapp.config import Config
from webapp.db import db, ma
from webapp.extensions.celery_utils import init_celery
from webapp.extensions.flask_logs import LogSetup
from webapp.item.views import blueprint as item_blueprint
from webapp.user.models import User
from webapp.user.views import blueprint as user_blueprint

PKG_NAME = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]


def create_app(app_name=PKG_NAME, **kwargs):
    """Создаем экземпляр приложения."""
    app = Flask(app_name)
    app.config.from_object(Config)

    if kwargs.get("celery"):
        init_celery(kwargs.get("celery"), app)

    db.init_app(app)
    ma.init_app(app)
    migrate = Migrate(app, db)  # noqa: F841

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'

    register_extensions(app)
    register_blueprints(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    @app.route('/index')
    def index():
        return redirect(url_for('user.login'))

    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()

    return app


def register_extensions(app):
    """Подключение расширений к flask-приложению."""
    logs = LogSetup()
    logs.init_app(app)
    return None


def register_blueprints(app):
    """Подключение блюпринтов к flask-приложению."""
    app.register_blueprint(user_blueprint)
    app.register_blueprint(worker_blueprint)
    app.register_blueprint(item_blueprint)
    return None
