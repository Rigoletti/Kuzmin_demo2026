from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, NumberRange
from datetime import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Логин обязателен'),
        Length(min=6, max=50, message='Логин должен быть от 6 до 50 символов'),
        Regexp(r'^[a-zA-Z0-9]+$', message='Только латинские буквы и цифры')
    ])

    last_name = StringField('Фамилия', validators=[
        DataRequired(message='Фамилия обязательна'),
        Length(min=2, max=50, message='От 2 до 50 символов'),
        Regexp(r'^[а-яА-Я\s-]+$', message='Только буквы кириллицы, пробелы и дефисы')
    ])

    first_name = StringField('Имя', validators=[
        DataRequired(message='Имя обязательно'),
        Length(min=2, max=50, message='От 2 до 50 символов'),
        Regexp(r'^[а-яА-Я\s-]+$', message='Только буквы кириллицы, пробелы и дефисы')
    ])

    patronymic = StringField('Отчество', validators=[
        DataRequired(message='Отчество обязательно'),
        Length(max=50, message='Не более 50 символов'),
        Regexp(r'^[а-яА-Я\s-]+$', message='Только буквы кириллицы, пробелы и дефисы')
    ])

    email = StringField('Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Некорректный email')
    ])

    phone = StringField('Телефон', validators=[
        DataRequired(message='Телефон обязателен'),
        Regexp(r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$', message='Формат: 8(XXX)XXX-XX-XX')
    ])

    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен'),
        Length(min=8, message='Пароль должен быть не менее 8 символов')
    ])

    confirm_password = PasswordField('Подтверждение пароля', validators=[
        DataRequired(message='Подтвердите пароль'),
        EqualTo('password', message='Пароли не совпадают')
    ])

    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Логин обязателен')
    ])

    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен')
    ])
    submit = SubmitField('Войти')

class RequestForm(FlaskForm):
    room_type = SelectField('Тип помещения', choices=[
        ('auditorium', 'Аудитория'),
        ('coworking', 'Коворкинг'),
        ('cinema', 'Кинозал')
    ], validators=[DataRequired(message='Выберите помещение')])

    start_date = DateField('Дата начала конференции', validators=[
        DataRequired(message='Дата обязательна')
    ], format='%d.%m.%Y')

    payment_method = SelectField('Способ оплаты', choices=[
        ('cash', 'Наличными'),
        ('transfer', 'Перевод по номеру телефона')
    ], validators=[DataRequired(message='Выберите способ оплаты')])

    submit = SubmitField('Забронировать')

class ReviewForm(FlaskForm):
    rating = IntegerField('Оценка (от 1 до 5)', validators=[
        DataRequired(message='Оценка обязательна'),
        NumberRange(min=1, max=5, message='Оценка должна быть от 1 до 5')
    ])
    comment = TextAreaField('Ваш отзыв', validators=[
        DataRequired(message='Отзыв не может быть пустым'),
        Length(min=10, max=1000, message='От 10 до 1000 символов')
    ])
    submit = SubmitField('Оставить отзыв')