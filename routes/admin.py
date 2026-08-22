from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Trek, Staff, User, Booking
from utils import admin_required
from datetime import datetime

bp = Blueprint('admin', __name__)


@bp.route('/admin/dashboard')
@admin_required
def dashboard():
    total_treks = Trek.query.count()
    total_users = User.query.count()
    total_staff = Staff.query.count()
    total_bookings = Booking.query.count()
    recent_bookings = Booking.query.order_by(Booking.booking_id.desc()).limit(5).all()
    pending_staff = Staff.query.filter_by(approval_status='Pending').all()
    recent_treks = Trek.query.order_by(Trek.trek_id.desc()).limit(5).all()
    return render_template('admin/dashboard.html', total_treks=total_treks, total_users=total_users, total_staff=total_staff, total_bookings=total_bookings, recent_bookings=recent_bookings, pending_staff=pending_staff, recent_treks=recent_treks)


@bp.route('/admin/treks', methods=['GET', 'POST'])
@admin_required
def treks():
    search = request.args.get('search', '')
    query = Trek.query
    if search:
        query = query.filter(Trek.trek_name.contains(search))
    treks = query.order_by(Trek.trek_id.desc()).all()
    staff_members = Staff.query.filter_by(approval_status='Approved').all()
    if request.method == 'POST':
        trek_name = request.form.get('trek_name', '').strip()
        location = request.form.get('location', '').strip()
        difficulty = request.form.get('difficulty', '').strip()
        duration = request.form.get('duration', '').strip()
        available_slots = request.form.get('available_slots', '0')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        description = request.form.get('description', '').strip()
        if not trek_name or not location or not difficulty or not duration or not start_date or not end_date:
            flash('Please fill all required trek fields.', 'danger')
        else:
            try:
                trek = Trek(
                    trek_name=trek_name,
                    location=location,
                    difficulty=difficulty,
                    duration=duration,
                    available_slots=int(available_slots),
                    start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
                    end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
                    description=description,
                    status='Pending'
                )
                if trek.available_slots < 0:
                    flash('Slots cannot be negative.', 'danger')
                    return redirect(url_for('admin.treks'))
                if trek.end_date < trek.start_date:
                    flash('End date cannot be before start date.', 'danger')
                    return redirect(url_for('admin.treks'))
                db.session.add(trek)
                db.session.commit()
                flash('Trek created successfully.', 'success')
                return redirect(url_for('admin.treks'))
            except ValueError:
                flash('Please enter valid dates and slot numbers.', 'danger')
    return render_template('admin/treks.html', treks=treks, staff_members=staff_members, search=search)


@bp.route('/admin/treks/<int:trek_id>/approve', methods=['POST'])
@admin_required
def approve_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    trek.status = 'Open'
    db.session.commit()
    flash('Trek approved and opened for booking.', 'success')
    return redirect(url_for('admin.treks'))


@bp.route('/admin/treks/<int:trek_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if request.method == 'POST':
        trek.trek_name = request.form.get('trek_name', '').strip() or trek.trek_name
        trek.location = request.form.get('location', '').strip() or trek.location
        trek.difficulty = request.form.get('difficulty', '').strip() or trek.difficulty
        trek.duration = request.form.get('duration', '').strip() or trek.duration
        trek.description = request.form.get('description', '').strip()
        trek.available_slots = int(request.form.get('available_slots', trek.available_slots))
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        if start_date:
            trek.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            trek.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        if trek.available_slots < 0:
            flash('Slots cannot be negative.', 'danger')
            return redirect(url_for('admin.edit_trek', trek_id=trek_id))
        if trek.end_date < trek.start_date:
            flash('End date cannot be before start date.', 'danger')
            return redirect(url_for('admin.edit_trek', trek_id=trek_id))
        db.session.commit()
        flash('Trek updated successfully.', 'success')
        return redirect(url_for('admin.treks'))
    return render_template('admin/edit_trek.html', trek=trek)


@bp.route('/admin/treks/<int:trek_id>/delete', methods=['POST'])
@admin_required
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    bookings = Booking.query.filter_by(trek_id=trek.trek_id).all()
    for booking in bookings:
        db.session.delete(booking)
    db.session.delete(trek)
    db.session.commit()
    flash('Trek deleted successfully.', 'success')
    return redirect(url_for('admin.treks'))


@bp.route('/admin/treks/<int:trek_id>/assign_staff', methods=['POST'])
@admin_required
def assign_staff(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    staff_id = request.form.get('staff_id')
    if staff_id:
        trek.assigned_staff_id = int(staff_id)
        trek.status = 'Open'
        db.session.commit()
        flash('Staff assigned successfully.', 'success')
    else:
        flash('Please select a staff member.', 'danger')
    return redirect(url_for('admin.treks'))


@bp.route('/admin/staff')
@admin_required
def staff():
    search = request.args.get('search', '')
    query = Staff.query
    if search:
        query = query.filter(Staff.name.contains(search) | Staff.email.contains(search))
    staff_members = query.order_by(Staff.staff_id.desc()).all()
    return render_template('admin/staff.html', staff_members=staff_members, search=search)


@bp.route('/admin/staff/<int:staff_id>/approve', methods=['POST'])
@admin_required
def approve_staff(staff_id):
    staff_member = Staff.query.get_or_404(staff_id)
    staff_member.approval_status = 'Approved'
    db.session.commit()
    flash('Staff approved.', 'success')
    return redirect(url_for('admin.staff'))


@bp.route('/admin/staff/<int:staff_id>/reject', methods=['POST'])
@admin_required
def reject_staff(staff_id):
    staff_member = Staff.query.get_or_404(staff_id)
    staff_member.approval_status = 'Rejected'
    staff_member.account_status = 'Inactive'
    db.session.commit()
    flash('Staff rejected.', 'danger')
    return redirect(url_for('admin.staff'))


@bp.route('/admin/users')
@admin_required
def users():
    search = request.args.get('search', '')
    query = User.query
    if search:
        query = query.filter(User.name.contains(search) | User.email.contains(search))
    users = query.order_by(User.user_id.desc()).all()
    return render_template('admin/users.html', users=users, search=search)


@bp.route('/admin/users/<int:user_id>/blacklist', methods=['POST'])
@admin_required
def blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.account_status = 'Blacklisted'
    db.session.commit()
    flash('User blacklisted successfully.', 'warning')
    return redirect(url_for('admin.users'))


@bp.route('/admin/users/<int:user_id>/whitelist', methods=['POST'])
@admin_required
def whitelist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.account_status = 'Active'
    db.session.commit()
    flash('User whitelisted successfully.', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/admin/bookings')
@admin_required
def bookings():
    bookings = Booking.query.order_by(Booking.booking_id.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)
