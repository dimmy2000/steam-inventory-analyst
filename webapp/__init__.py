# -*- coding: utf-8 -*-
from datetime import datetime

from flask import Flask, redirect, url_for

from flask_login import LoginManager, current_user

from webapp.db import db

from webapp.config import Config
from webapp.user.models import User
from webapp.user.routes import blueprint as user_blueprint
from webapp.worker.routes import blueprint as worker_blueprint

# Создаем экземпляр приложения.
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

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
