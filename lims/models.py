from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(50))
    record_id = db.Column(db.Integer)
    field_name = db.Column(db.String(50))
    old_value = db.Column(db.String(255))
    new_value = db.Column(db.String(255))
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='analyst')

    def __repr__(self):
        return f'<User {self.username}>'


class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_number = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    received_date = db.Column(db.Date)
    released = db.Column(db.Boolean, default=False)

    tests = db.relationship('Test', backref='sample', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Sample {self.job_number}>'


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.Integer, db.ForeignKey('sample.id'), nullable=False)
    test_name = db.Column(db.String(120))
    method = db.Column(db.String(120))
    specification = db.Column(db.String(120))
    result = db.Column(db.String(120))
    analyst_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    checker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    released = db.Column(db.Boolean, default=False)

    analyst = db.relationship('User', foreign_keys=[analyst_id], backref='analysed_tests')
    checker = db.relationship('User', foreign_keys=[checker_id], backref='checked_tests')

    def __repr__(self):
        return f'<Test {self.test_name}>'
