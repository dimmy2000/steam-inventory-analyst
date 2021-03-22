from webapp.user.models import User

from flask_wtf import FlaskForm

from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()],
                           render_kw={"class": "form-control"})
    password = PasswordField('Пароль', validators=[DataRequired()],
                             render_kw={"class": "form-control"})
    remember_me = BooleanField('Запомнить меня',
                               render_kw={"class": "form-check-input"})
    submit = SubmitField('Отправить', render_kw={"class": "btn btn-primary"})


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()],
                           render_kw={"class": "form-control"})
    email = StringField('Адрес эл. почты', validators=[DataRequired(), Email()],
                        render_kw={"class": "form-control"})
    password = PasswordField('Пароль', validators=[DataRequired()],
                             render_kw={"class": "form-control"})
    password2 = PasswordField('Повторите пароль',
                              validators=[DataRequired(),
                                          EqualTo('password')],
                              render_kw={"class": "form-control"})
    submit = SubmitField('Отправить', render_kw={"class": "btn btn-primary"})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста используйте другое имя'
                                  'пользователя.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста используйте другой адрес'
                                  'эл. почты.')
