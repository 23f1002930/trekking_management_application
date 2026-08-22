from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user, login_required


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'role', None) != 'admin':
            flash('Only administrators can access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return wrapped


def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'role', None) != 'staff':
            flash('Only staff members can access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return wrapped


def user_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'role', None) != 'user':
            flash('Only users can access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return wrapped
