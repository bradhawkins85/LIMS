# LIMS

A minimal Laboratory Information Management System using Flask and MySQL (via SQLAlchemy). This prototype replaces an MS Access database with a web interface and includes basic audit logging and role-based permissions.

## Features

- Manage samples and associated tests
- Change logging with user and timestamp stored in `AuditLog`
- Role-based permissions: only admin can un-release samples; analyst and checker must differ
- Tests become read-only once a sample is released

## Setup

```bash
pip install -r requirements.txt  # optional; or install Flask, Flask-Login, Flask-SQLAlchemy, PyMySQL
flask --app lims.app:create_app init-db  # creates SQLite database and admin user
flask --app lims.app:create_app run --host 0.0.0.0
```

The app uses SQLite by default. Set the `DATABASE_URI` environment variable to connect to MySQL, for example:

```bash
export DATABASE_URI="mysql+pymysql://user:password@localhost/lims"
```

Then run `flask --app lims.app:create_app run --host 0.0.0.0`.

Login with username `admin` and password `admin`.
