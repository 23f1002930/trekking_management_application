from datetime import datetime, date
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from config import ADMIN_EMAIL, ADMIN_PASSWORD, ALLOWED_DIFFICULTIES


db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    account_status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        # Return a namespaced id so Flask-Login can distinguish user types
        return f"user-{self.user_id}"


class Staff(UserMixin, db.Model):
    __tablename__ = 'staff'

    staff_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='staff')
    approval_status = db.Column(db.String(20), default='Pending')
    account_status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        # Return a namespaced id so Flask-Login can distinguish user types
        return f"staff-{self.staff_id}"


class Trek(db.Model):
    __tablename__ = 'treks'

    trek_id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    available_slots = db.Column(db.Integer, nullable=False, default=0)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=True)
    status = db.Column(db.String(20), default='Pending')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assigned_staff = db.relationship('Staff', backref='treks')


class Booking(db.Model):
    __tablename__ = 'bookings'

    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.trek_id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Booked')

    user = db.relationship('User', backref='bookings')
    trek = db.relationship('Trek', backref='bookings')


def init_database(app):
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(email=ADMIN_EMAIL).first()
        if not admin:
            admin = User(name='Admin', email=ADMIN_EMAIL, phone='', role='admin', account_status='Active')
            admin.set_password(ADMIN_PASSWORD)
            db.session.add(admin)

        if not Staff.query.filter_by(email='staff@example.com').first():
            staff = Staff(name='Demo Staff', email='staff@example.com', phone='9876543210', approval_status='Approved', account_status='Active')
            staff.set_password('Staff@123')
            db.session.add(staff)

        if not User.query.filter_by(email='user@example.com').first():
            user = User(name='Demo User', email='user@example.com', phone='9123456780', role='user', account_status='Active')
            user.set_password('User@123')
            db.session.add(user)

        if not Trek.query.first():
            trek = Trek(
                trek_name='Everest Base Camp Trek',
                location='Nepal',
                difficulty='Hard',
                duration='10 Days',
                available_slots=8,
                assigned_staff_id=Staff.query.filter_by(email='staff@example.com').first().staff_id if Staff.query.filter_by(email='staff@example.com').first() else None,
                status='Open',
                start_date=date(2026, 10, 1),
                end_date=date(2026, 10, 10),
                description='A famous trek for beginners and advanced trekkers.'
            )
            db.session.add(trek)

        if not Booking.query.first():
            demo_user = User.query.filter_by(email='user@example.com').first()
            demo_trek = Trek.query.filter_by(trek_name='Everest Base Camp Trek').first()
            if demo_user and demo_trek:
                booking = Booking(user_id=demo_user.user_id, trek_id=demo_trek.trek_id, status='Booked')
                db.session.add(booking)
                demo_trek.available_slots -= 1

        db.session.commit()
