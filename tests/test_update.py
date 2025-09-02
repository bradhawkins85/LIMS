import subprocess

from werkzeug.security import generate_password_hash

from lims.app import create_app
from lims.models import db, User


def create_test_app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test',
    })
    with app.app_context():
        db.create_all()
        admin = User(username='admin', password=generate_password_hash('admin'), role='admin')
        db.session.add(admin)
        db.session.commit()
    return app


def test_update_handles_missing_git(monkeypatch):
    app = create_test_app()
    client = app.test_client()
    # Log in as admin
    client.post('/login', data={'username': 'admin', 'password': 'admin'})

    def fake_run(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, 'run', fake_run)

    response = client.get('/update')
    assert response.status_code == 302
    with client.session_transaction() as sess:
        flashes = sess.get('_flashes', [])
    assert any('git is not installed' in message for category, message in flashes)
