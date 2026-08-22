from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Staff
from config import ADMIN_EMAIL, ADMIN_PASSWORD

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            admin_user = User.query.filter_by(email=ADMIN_EMAIL).first()
            if admin_user is None:
                admin_user = User(name='Admin', email=ADMIN_EMAIL, phone='', role='admin', account_status='Active')
                admin_user.set_password(ADMIN_PASSWORD)
                db.session.add(admin_user)
                db.session.commit()
            login_user(admin_user)
            flash('Admin login successful.', 'success')
            return redirect(url_for('admin.dashboard'))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.account_status != 'Active':
                flash('Your account is not active.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user)
            flash('User login successful.', 'success')
            return redirect(url_for('user.dashboard'))

        staff = Staff.query.filter_by(email=email).first()
        if staff and staff.check_password(password):
            if staff.approval_status != 'Approved':
                flash('Your staff account is waiting for admin approval.', 'danger')
                return redirect(url_for('auth.login'))
            if staff.account_status != 'Active':
                flash('Your staff account is not active.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(staff)
            flash('Staff login successful.', 'success')
            return redirect(url_for('staff.dashboard'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('Name, email and password are required.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('A user with that email already exists.', 'danger')
        else:
            user = User(name=name, email=email, phone=phone, role='user', account_status='Active')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('register_user.html')


@bp.route('/register-staff', methods=['GET', 'POST'])
def register_staff():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('Name, email and password are required.', 'danger')
        elif Staff.query.filter_by(email=email).first():
            flash('A staff member with that email already exists.', 'danger')
        else:
            staff = Staff(name=name, email=email, phone=phone, role='staff', approval_status='Pending', account_status='Active')
            staff.set_password(password)
            db.session.add(staff)
            db.session.commit()
            flash('Staff registration submitted. Please wait for admin approval.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('register_staff.html')
