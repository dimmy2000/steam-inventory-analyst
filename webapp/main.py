"""Основная структура flask-приложения.

Здесь создается экземпляр flask-приложения, сессия для работы с БД,
подтягиваются блюпринты для реализации логики.
"""
# -*- coding: utf-8 -*-
import gevent
from gevent import monkey  # noqa: F401
gevent.monkey.patch_all()

from datetime import datetime  # noqa: E402, I100

from flask import Flask, redirect, url_for  # noqa: E402
from flask_login import LoginManager, current_user  # noqa: E402
from flask_migrate import Migrate  # noqa: E402

from webapp import db  # noqa: E402
from webapp.account.routes import blueprint as worker_blueprint  # noqa: E402
from webapp.config import Config  # noqa: E402
from webapp.user.models import User  # noqa: E402
from webapp.user.routes import blueprint as user_blueprint  # noqa: E402


def create_app():
    """Создаем экземпляр приложения."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'

    app.register_blueprint(user_blueprint)
    app.register_blueprint(worker_blueprint)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        return redirect(url_for('user.login'))

    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()

    return app


if __name__ == '__main__':
    flask_app = create_app()
    flask_app.run(debug=True)
