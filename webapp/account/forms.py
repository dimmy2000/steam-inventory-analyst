"""Реализация форм для работы с воркерами."""
from flask_wtf import FlaskForm

from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class SteamLoginForm(FlaskForm):
    """Форма авторизации воркера.

    Передаем в нее логин и пароль пользователя Steam, опционально передаем
    необходимую информацию (код из е-мэйла, код из мобильного приложения).
    """

    username = StringField('Имя пользователя Steam:',
                           validators=[DataRequired()],
                           render_kw={"class": "form-control"})
    password = PasswordField('Пароль:',
                             validators=[DataRequired()],
                             render_kw={"class": "form-control"})
    auth_code = StringField('Введите код, высланный на ваш e-mail:',
                            render_kw={"class": "form-control"})
    two_factor_code = StringField('Введите код из мобильного приложения '
                                  'Steam:',
                                  render_kw={"class": "form-control"})
    submit = SubmitField('Отправить',
                         render_kw={"class": "btn btn-success",
                                    "data-bs-dismiss": "modal",
                                    "onclick": "form_submit()"})
