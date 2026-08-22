from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from models import db, Trek, Booking, User
from utils import user_required

bp = Blueprint('user', __name__)


@bp.route('/user/dashboard')
@user_required
def dashboard():
    treks = Trek.query.filter_by(status='Open').all()
    bookings = Booking.query.filter_by(user_id=current_user.user_id).order_by(Booking.booking_id.desc()).limit(5).all()
    return render_template('user/dashboard.html', treks=treks, upcoming_bookings=bookings)


@bp.route('/user/treks')
@user_required
def treks():
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    difficulty = request.args.get('difficulty', '')

    query = Trek.query.filter_by(status='Open')
    if search:
        query = query.filter(Trek.trek_name.contains(search))
    if location:
        query = query.filter(Trek.location.contains(location))
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)

    treks = query.order_by(Trek.trek_id.desc()).all()
    return render_template('user/treks.html', treks=treks, search=search, location=location, difficulty=difficulty)


@bp.route('/user/treks/<int:trek_id>')
@user_required
def trek_details(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    return render_template('user/trek_details.html', trek=trek)


@bp.route('/user/treks/<int:trek_id>/book', methods=['POST'])
@user_required
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    user = User.query.get_or_404(current_user.user_id)

    if user.account_status != 'Active':
        flash('Your account is not active.', 'danger')
        return redirect(url_for('user.treks'))
    if trek.status != 'Open':
        flash('This trek is not open for booking.', 'danger')
        return redirect(url_for('user.treks'))
    if trek.available_slots <= 0:
        flash('This trek is already full.', 'danger')
        return redirect(url_for('user.treks'))

    existing = Booking.query.filter_by(user_id=user.user_id, trek_id=trek.trek_id, status='Booked').first()
    if existing:
        flash('You have already booked this trek.', 'danger')
        return redirect(url_for('user.treks'))

    booking = Booking(user_id=user.user_id, trek_id=trek.trek_id, status='Booked')
    db.session.add(booking)
    trek.available_slots -= 1
    db.session.commit()
    flash('Booking successful.', 'success')
    return redirect(url_for('user.bookings'))


@bp.route('/user/bookings')
@user_required
def bookings():
    bookings = Booking.query.filter_by(user_id=current_user.user_id).order_by(Booking.booking_id.desc()).all()
    return render_template('user/bookings.html', bookings=bookings)


@bp.route('/user/bookings/<int:booking_id>/cancel', methods=['POST'])
@user_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.user_id:
        flash('You can only cancel your own bookings.', 'danger')
        return redirect(url_for('user.bookings'))
    if booking.status != 'Booked':
        flash('This booking is already not active.', 'danger')
        return redirect(url_for('user.bookings'))
    booking.status = 'Cancelled'
    booking.trek.available_slots += 1
    db.session.commit()
    flash('Booking cancelled successfully.', 'success')
    return redirect(url_for('user.bookings'))


@bp.route('/user/history')
@user_required
def history():
    bookings = Booking.query.filter_by(user_id=current_user.user_id).order_by(Booking.booking_id.desc()).all()
    return render_template('user/history.html', bookings=bookings)


@bp.route('/user/profile', methods=['GET', 'POST'])
@user_required
def profile():
    user = User.query.get_or_404(current_user.user_id)
    if request.method == 'POST':
        user.name = request.form.get('name', '').strip() or user.name
        user.phone = request.form.get('phone', '').strip()
        db.session.commit()
        flash('Profile updated.', 'success')
    return render_template('user/profile.html', user=user)
