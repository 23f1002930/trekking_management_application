import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'trekking.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


ADMIN_EMAIL = 'admin@example.com'
ADMIN_PASSWORD = 'Admin@123'
ALLOWED_DIFFICULTIES = ['Easy', 'Moderate', 'Hard']
