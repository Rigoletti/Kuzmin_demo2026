from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Request, Review
from forms import RegistrationForm, LoginForm, RequestForm, ReviewForm
from sqlalchemy.exc import IntegrityError
import re
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kuzminfdfdfdfgxxcccgre34'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conference.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def normalize_phone(phone):
    return re.sub(r'\D', '', phone)

@app.context_processor
def utility_processor():
    def get_status_color(status):
        colors = {
            'new': 'warning',
            'appointed': 'primary',
            'completed': 'success'
        }
        return colors.get(status, 'secondary')

    def get_status_name(status):
        names = {
            'new': 'Новая',
            'appointed': 'Мероприятие назначено',
            'completed': 'Мероприятие завершено'
        }
        return names.get(status, status)

    def get_room_name(room_type):
        rooms = {
            'auditorium': 'Аудитория',
            'coworking': 'Коворкинг',
            'cinema': 'Кинозал'
        }
        return rooms.get(room_type, room_type)

    return dict(get_status_color=get_status_color, get_status_name=get_status_name, get_room_name=get_room_name)

@app.route('/')
def index():
    total_users = User.query.filter_by(is_admin=False).count()
    total_requests = Request.query.count()
    completed_requests = Request.query.filter_by(status='completed').count()
    latest_requests = Request.query.order_by(Request.created_at.desc()).limit(5).all()

    return render_template('index.html',
                           total_users=total_users,
                           total_requests=total_requests,
                           completed_requests=completed_requests,
                           latest_requests=latest_requests)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Пользователь с таким логином уже существует', 'danger')
            return render_template('register.html', form=form)

        existing_email = User.query.filter_by(email=form.email.data.lower()).first()
        if existing_email:
            flash('Пользователь с таким email уже существует', 'danger')
            return render_template('register.html', form=form)

        clean_phone = normalize_phone(form.phone.data)

        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            last_name=form.last_name.data.strip(),
            first_name=form.first_name.data.strip(),
            patronymic=form.patronymic.data.strip(),
            phone=clean_phone,
            is_admin=False
        )

        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Регистрация успешна! Теперь вы можете войти', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Ошибка при регистрации', 'danger')
            return render_template('register.html', form=form)

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        # вход для админа
        if form.username.data == 'Admin26' and form.password.data == 'Demo20':
            admin = User.query.filter_by(username='Admin26').first()
            if not admin:
                admin = User(
                    username='Admin26',
                    email='admin@conference.ru',
                    last_name='Администратор',
                    first_name='Системный',
                    patronymic='',
                    phone='80000000000',
                    is_admin=True
                )
                admin.set_password('Demo20')
                db.session.add(admin)
                db.session.commit()
            login_user(admin)
            flash('Добро пожаловать в панель администратора!', 'success')
            return redirect(url_for('admin.admin_dashboard'))

        # обычный вход через логин
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'С возвращением, {user.get_short_name()}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверный логин или пароль', 'danger')

    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))

    user_requests = Request.query.filter_by(user_id=current_user.id).order_by(Request.created_at.desc()).all()
    total_requests = len(user_requests)
    new_requests = len([r for r in user_requests if r.status == 'new'])
    appointed_requests = len([r for r in user_requests if r.status == 'appointed'])
    completed_requests = len([r for r in user_requests if r.status == 'completed'])

    return render_template('dashboard.html',
                           user=current_user,
                           requests=user_requests,
                           total_requests=total_requests,
                           new_requests=new_requests,
                           appointed_requests=appointed_requests,
                           completed_requests=completed_requests)

@app.route('/create-request', methods=['GET', 'POST'])
@login_required
def create_request():
    if current_user.is_admin:
        flash('Администраторы не могут создавать заявки', 'warning')
        return redirect(url_for('admin.admin_dashboard'))

    form = RequestForm()
    if form.validate_on_submit():
        request_obj = Request(
            room_type=form.room_type.data,
            start_date=form.start_date.data,
            payment_method=form.payment_method.data,
            user_id=current_user.id,
            status='new'
        )
        db.session.add(request_obj)
        db.session.commit()
        flash('Заявка успешно создана и отправлена на согласование администратору!', 'success')
        return redirect(url_for('my_requests'))

    return render_template('create_request.html', form=form)

@app.route('/my-requests')
@login_required
def my_requests():
    if current_user.is_admin:
        return redirect(url_for('admin.admin_requests'))

    requests = Request.query.filter_by(user_id=current_user.id).order_by(Request.created_at.desc()).all()
    return render_template('my_requests.html', requests=requests)

@app.route('/request/<int:request_id>/review', methods=['GET', 'POST'])
@login_required
def leave_review(request_id):
    if current_user.is_admin:
        flash('Администраторы не могут оставлять отзывы', 'warning')
        return redirect(url_for('admin.admin_dashboard'))

    req = Request.query.get_or_404(request_id)
    if req.user_id != current_user.id:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('my_requests'))

    existing_review = Review.query.filter_by(request_id=request_id, user_id=current_user.id).first()
    if existing_review:
        flash('Вы уже оставили отзыв на эту заявку', 'warning')
        return redirect(url_for('my_requests'))

    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            rating=form.rating.data,
            comment=form.comment.data,
            user_id=current_user.id,
            request_id=request_id
        )
        db.session.add(review)
        db.session.commit()
        flash('Спасибо за ваш отзыв!', 'success')
        return redirect(url_for('my_requests'))

    return render_template('review_form.html', form=form, request=req)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

from admin import admin_bp

app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # создание админа 
        admin = User.query.filter_by(username='Admin26').first()
        if not admin:
            admin = User(
                username='Admin26',
                email='admin@conference.ru',
                last_name='Администратор',
                first_name='Системный',
                patronymic='',
                phone='80000000000',
                is_admin=True
            )
            admin.set_password('Demo20')
            db.session.add(admin)
            db.session.commit()
            print("Администратор создан: Admin26 / Demo20")
    app.run(debug=True)