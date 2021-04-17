"""Реализация разделов сайта для работы с предметами сообщества Steam."""
import os

from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user

from webapp.account.models import Account

blueprint = Blueprint('item', __name__,
                      url_prefix='/items')


@blueprint.route('/<steam_login>/items/<item_id>')
@login_required
def item_description(steam_login, item_id):
    """Описание предмета из коллекции Steam."""
    title = 'title'
    account = Account.query.filter_by(username=steam_login,
                                      user_id=current_user.user_id).first()
    item = account.items.filter_by(asset_id=item_id).first()
    description = item.descriptions
    template_path = os.path.join('item', 'item.html')
    return render_template(template_path, title=title, account=account,
                           description=description,
                           )
