import os

from flask import Flask
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

from .models import db, User
from .auth import bp as auth_bp
from .main import bp as main_bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'dev'
    os.makedirs(app.instance_path, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        app.config.get('DATABASE_URI')
        or f"sqlite:///{os.path.join(app.instance_path, 'lims.db')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.cli.command('init-db')
    def init_db():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
        print('Database initialized')

    return app
