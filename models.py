from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    patronymic = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requests = db.relationship('Request', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    def get_short_name(self):
        return f"{self.last_name} {self.first_name[0]}. {self.patronymic[0]}."

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_type = db.Column(db.String(50), nullable=False)  # аудитория, коворкинг, кинозал
    start_date = db.Column(db.Date, nullable=False) 
    payment_method = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def get_room_name(self):
        rooms = {
            'auditorium': 'Аудитория',
            'coworking': 'Коворкинг',
            'cinema': 'Кинозал'
        }
        return rooms.get(self.room_type, self.room_type)

    def get_payment_method_name(self):
        methods = {
            'cash': 'Наличными',
            'transfer': 'Перевод по номеру телефона'
        }
        return methods.get(self.payment_method, self.payment_method)

    def get_status_name(self):
        statuses = {
            'new': 'Новая',
            'appointed': 'Мероприятие назначено',
            'completed': 'Мероприятие завершено'
        }
        return statuses.get(self.status, self.status)

    def get_status_color(self):
        colors = {
            'new': 'warning',
            'appointed': 'primary',
            'completed': 'success'
        }
        return colors.get(self.status, 'secondary')


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('request.id'), nullable=False)

    request = db.relationship('Request', backref='reviews')