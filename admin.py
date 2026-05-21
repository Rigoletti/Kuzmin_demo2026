from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Request
from functools import wraps

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Доступ запрещен. Требуются права администратора.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.filter_by(is_admin=False).count()
    total_requests = Request.query.count()
    new_requests = Request.query.filter_by(status='new').count()
    appointed_requests = Request.query.filter_by(status='appointed').count()
    completed_requests = Request.query.filter_by(status='completed').count()

    latest_requests = Request.query.order_by(Request.created_at.desc()).limit(10).all()
    latest_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_requests=total_requests,
                           new_requests=new_requests,
                           appointed_requests=appointed_requests,
                           completed_requests=completed_requests,
                           latest_requests=latest_requests,
                           latest_users=latest_users)


@admin_bp.route('/requests')
@login_required
@admin_required
def admin_requests():
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # постраничная навигация

    if status_filter == 'all':
        pagination = Request.query.order_by(Request.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        requests = pagination.items
    else:
        pagination = Request.query.filter_by(status=status_filter).order_by(Request.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        requests = pagination.items

    return render_template('admin/requests.html', 
                           requests=requests, 
                           current_filter=status_filter,
                           pagination=pagination)


@admin_bp.route('/request/<int:request_id>/status/<string:new_status>', methods=['POST'])
@login_required
@admin_required
def change_request_status(request_id, new_status):
    if new_status not in ['new', 'appointed', 'completed']:
        flash('Некорректный статус', 'danger')
        return redirect(url_for('admin.admin_requests'))

    req = Request.query.get_or_404(request_id)
    req.status = new_status
    db.session.commit()

    status_names = {'new': 'Новая', 'appointed': 'Мероприятие назначено', 'completed': 'Мероприятие завершено'}
    flash(f'Статус заявки "{req.get_room_name()}" изменен на "{status_names[new_status]}"', 'success')
    return redirect(url_for('admin.admin_requests'))
