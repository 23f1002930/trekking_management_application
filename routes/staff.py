from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from models import db, Trek, Booking
from utils import staff_required

bp = Blueprint('staff', __name__)


@bp.route('/staff/dashboard')
@staff_required
def dashboard():
    assigned_treks = Trek.query.filter_by(assigned_staff_id=current_user.staff_id).all()
    participant_count = 0
    for trek in assigned_treks:
        participant_count += Booking.query.filter_by(trek_id=trek.trek_id).count()
    return render_template('staff/dashboard.html', assigned_treks=assigned_treks, participant_count=participant_count)


@bp.route('/staff/treks')
@staff_required
def treks():
    assigned_treks = Trek.query.filter_by(assigned_staff_id=current_user.staff_id).all()
    return render_template('staff/treks.html', assigned_treks=assigned_treks)


@bp.route('/staff/treks/<int:trek_id>/participants')
@staff_required
def participants(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.staff_id:
        flash('You cannot manage a trek that is not assigned to you.', 'danger')
        return redirect(url_for('staff.treks'))
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    return render_template('staff/participants.html', trek=trek, bookings=bookings)


@bp.route('/staff/treks/<int:trek_id>/update', methods=['GET', 'POST'])
@staff_required
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.staff_id:
        flash('You cannot manage a trek that is not assigned to you.', 'danger')
        return redirect(url_for('staff.treks'))

    if request.method == 'POST':
        available_slots = request.form.get('available_slots', '0')
        status = request.form.get('status', trek.status)
        try:
            trek.available_slots = int(available_slots)
            if trek.available_slots < 0:
                flash('Slots cannot be negative.', 'danger')
                return redirect(url_for('staff.update_trek', trek_id=trek_id))
            trek.status = status
            db.session.commit()
            flash('Trek updated successfully.', 'success')
            return redirect(url_for('staff.treks'))
        except ValueError:
            flash('Please enter a valid slot number.', 'danger')

    return render_template('staff/update_trek.html', trek=trek)


@bp.route('/staff/treks/<int:trek_id>/complete', methods=['POST'])
@staff_required
def complete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.staff_id:
        flash('You cannot manage a trek that is not assigned to you.', 'danger')
        return redirect(url_for('staff.treks'))
    trek.status = 'Completed'
    db.session.commit()
    flash('Trek marked as completed.', 'success')
    return redirect(url_for('staff.treks'))
