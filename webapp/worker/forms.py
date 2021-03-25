from flask_wtf import FlaskForm

from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class AddWorkerForm(FlaskForm):
    username = StringField('Имя аккаунта Steam', validators=[DataRequired()],
                           render_kw={"class": "form-control"})
    password = PasswordField('Пароль', validators=[DataRequired()],
                             render_kw={"class": "form-control"})
    auth_code = StringField('Введите код, высланный на ваш e-mail')
    two_factor_code = StringField('Введите код из мобильного приложения '
                                  'Steam')
    submit = SubmitField('Отправить', render_kw={"class": "btn btn-success"})
