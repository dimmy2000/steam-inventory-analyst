from flask import Blueprint, render_template

from flask_login import current_user, login_required

from webapp.worker.forms import AddWorkerForm

blueprint = Blueprint('worker', __name__,
                      url_prefix='/workers')


@blueprint.route('/add_worker')
@login_required
def worker_login():
    title = 'Подключение воркера'
    form = AddWorkerForm()
    return render_template('worker/add_worker.html', title=title, form=form)
