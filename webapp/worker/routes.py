from flask import Blueprint, flash, render_template

from flask_login import login_required

from steam.enums import EResult

from webapp.worker.forms import AddWorkerForm

blueprint = Blueprint('worker', __name__,
                      url_prefix='/workers')


@blueprint.route('/add_worker', methods=['GET', 'POST'])
@login_required
def worker_login():
    title = 'Подключение воркера'
    form = AddWorkerForm()

    login_key = None
    auth_code = None
    two_factor_code = None
    if form.validate_on_submit():
        user_login = form.username.data
        password = form.password.data
        login = f'login({user_login}, {password}, {login_key}, {auth_code}, {two_factor_code})'
        flash(login, 'primary')
        result = EResult.TwoFactorCodeMismatch
        if result == EResult.TwoFactorCodeMismatch:
            flash(str(result), 'EResult')
            two_factor_code = form.two_factor_code.data
            login = f'login({user_login}, {password}, {login_key}, {auth_code}, {two_factor_code})'
            flash(login, 'primary')

    return render_template('worker/add_worker.html', title=title, form=form)
