from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    username = StringField('Логин (E-mail)', validators=[DataRequired('Это обязательное поле'),
                                                         Email('Некорректный формат E-mail'),
                                                         Length(max=25,
                                                                message='Email должен быть не больше 25 символов')])
    password = PasswordField('Пароль', validators=[DataRequired('Пароль обязателен'),
                                                   Length(min=6, max=30,
                                                          message='Пароль должен быть от 6 до 30 символов')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
