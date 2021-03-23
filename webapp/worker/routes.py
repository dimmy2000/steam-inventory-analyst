from flask import Blueprint, render_template

from flask_login import current_user, login_required

from webapp import User
from webapp.worker.forms import AddWorkerForm

blueprint = Blueprint('worker', __name__,
                      url_prefix='/workers')


@blueprint.route('/add_worker')
@login_required
def worker_login():
    title = 'Регистрация воркера'
    user = User.query.filter_by(username=current_user.username).first_or_404()
    return render_template('worker/add_worker.html', user=user, title=title)
