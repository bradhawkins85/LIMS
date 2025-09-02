# LIMS

A minimal Laboratory Information Management System using Flask and MySQL (via SQLAlchemy). This prototype replaces an MS Access database with a web interface and includes basic audit logging and role-based permissions.

## Features

- Manage samples and associated tests
- Change logging with user and timestamp stored in `AuditLog`
- Role-based permissions: only admin can un-release samples; analyst and checker must differ
- Tests become read-only once a sample is released

## Prerequisites

If your environment is missing Git or Python tooling, install the necessary packages:

```bash
sudo apt install git python3-pip python3.12-venv
```

## Setup

Debian-based systems may report an "externally managed environment" when using `pip` globally. Create and use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

After installing the dependencies, initialize the database and start the app:

```bash
flask --app lims.app create-app init-db  # creates SQLite database and admin user
flask --app lims.app run
```

When you're done, exit the virtual environment with `deactivate`.

The app uses SQLite by default. Set the `DATABASE_URI` environment variable to connect to MySQL, for example:

```bash
export DATABASE_URI="mysql+pymysql://user:password@localhost/lims"
```

Then run `flask --app lims.app run`.

Login with username `admin` and password `admin`.
