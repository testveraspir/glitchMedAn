from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired('Е-mail обязателен'),
                                            Email(message="Не корректный формат почты"),
                                            Length(max=25, message='Email должен быть не больше 25 символов')])
    password = PasswordField('Пароль', validators=[DataRequired('Вы не ввели пароль'),
                                                   Length(min=6, max=30,
                                                          message='Пароль должен быть от 6 до 30 символов')])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired('Введите подтверждение пароля'),
                                                                   Length(max=30)])
    name = StringField('Имя', validators=[DataRequired('Укажите своё Имя'),
                                          Length(min=2, max=25,
                                                 message='Имя пользователя должно быть от 2 до 25 символов')])
    lastname = StringField('Фамилия', validators=[DataRequired('Укажите свою Фамилию'),
                                                  Length(min=2, max=25,
                                                         message='Имя пользователя должно быть от 2 до 25 символов')])
    birthday = StringField('Дата рождения', validators=[DataRequired('Укажите дату рождения в формате: ДД.ММ.ГГГГ'),
                                                        Regexp(r'^(\d{2}).(\d{2}).(\d{4})$',
                                                               message='Укажите дату рождения в формате: ДД.ММ.ГГГГ')])
    gender = SelectField("Выберите пол",  choices=[('м', "Мужской"), ('ж', "Женский")])
    submit = SubmitField('Зарегистрироваться')
