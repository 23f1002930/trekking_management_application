from flask import Flask, redirect, url_for, request, flash
from flask_login import LoginManager, current_user
from config import Config
from models import db, User, Staff, init_database
from routes.auth import bp as auth_bp
from routes.admin import bp as admin_bp
from routes.staff import bp as staff_bp
from routes.user import bp as user_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(user_bp)


@login_manager.user_loader
def load_user(user_id):
    if user_id is None:
        return None
    # We store namespaced ids like 'user-1' or 'staff-2'. Parse them here.
    try:
        if isinstance(user_id, str) and user_id.startswith('user-'):
            real_id = int(user_id.split('-', 1)[1])
            return User.query.get(real_id)
        if isinstance(user_id, str) and user_id.startswith('staff-'):
            real_id = int(user_id.split('-', 1)[1])
            return Staff.query.get(real_id)
        # Fallback: try integer id (legacy)
        real_id = int(user_id)
        user = User.query.get(real_id)
        if user:
            return user
        return Staff.query.get(real_id)
    except Exception:
        return None


@app.route('/')
def index():
    return redirect(url_for('auth.login'))


@app.before_request
def protect_pages():
    if request.endpoint in {'auth.login', 'auth.register_user', 'auth.register_staff', 'static', 'index'}:
        return None
    if current_user.is_authenticated:
        return None
    if request.endpoint and request.endpoint.startswith(('admin.', 'staff.', 'user.')):
        flash('Please login to continue.', 'danger')
        return redirect(url_for('auth.login'))


def create_app():
    return app


if __name__ == '__main__':
    init_database(app)
    app.run(debug=True)
