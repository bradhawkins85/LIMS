from datetime import date
import os
import subprocess
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from .models import db, Sample, Test, User, AuditLog

bp = Blueprint('main', __name__)


def log_change(table, record_id, field, old, new):
    if old == new:
        return
    entry = AuditLog(
        table_name=table,
        record_id=record_id,
        field_name=field,
        old_value=str(old) if old is not None else '',
        new_value=str(new) if new is not None else '',
        changed_by=current_user.id if current_user.is_authenticated else None,
    )
    db.session.add(entry)


@bp.route('/')
@login_required
def index():
    return redirect(url_for('main.sample_list'))


@bp.route('/samples')
@login_required
def sample_list():
    samples = Sample.query.all()
    return render_template('samples.html', samples=samples)


@bp.route('/sample/<int:sample_id>', methods=['GET', 'POST'])
@login_required
def sample_detail(sample_id):
    sample = Sample.query.get_or_404(sample_id)
    if request.method == 'POST':
        if sample.released and not current_user.role == 'admin':
            flash('Released samples cannot be edited.')
            return redirect(url_for('main.sample_detail', sample_id=sample_id))
        old_job = sample.job_number
        old_desc = sample.description
        old_date = sample.received_date
        old_released = sample.released
        sample.job_number = request.form['job_number']
        sample.description = request.form['description']
        sample.received_date = request.form['received_date'] or None
        sample.released = 'released' in request.form
        if old_released and not sample.released and current_user.role != 'admin':
            flash('Only admin can un-release a sample.')
            sample.released = True
        log_change('sample', sample.id, 'job_number', old_job, sample.job_number)
        log_change('sample', sample.id, 'description', old_desc, sample.description)
        log_change('sample', sample.id, 'received_date', old_date, sample.received_date)
        log_change('sample', sample.id, 'released', old_released, sample.released)
        db.session.commit()
        flash('Sample updated')
    return render_template('sample_detail.html', sample=sample)


@bp.route('/sample/new', methods=['GET', 'POST'])
@login_required
def sample_new():
    if request.method == 'POST':
        sample = Sample(
            job_number=request.form['job_number'],
            description=request.form['description'],
            received_date=request.form['received_date'] or None,
        )
        db.session.add(sample)
        db.session.commit()
        flash('Sample created')
        return redirect(url_for('main.sample_detail', sample_id=sample.id))
    return render_template('sample_detail.html', sample=None)


@bp.route('/sample/<int:sample_id>/add_test', methods=['POST'])
@login_required
def add_test(sample_id):
    sample = Sample.query.get_or_404(sample_id)
    if sample.released:
        flash('Cannot add tests to released sample')
        return redirect(url_for('main.sample_detail', sample_id=sample_id))
    test = Test(
        sample=sample,
        test_name=request.form['test_name'],
        method=request.form['method'],
        specification=request.form['specification'],
        result=request.form['result'],
        analyst_id=request.form['analyst_id'] or None,
        checker_id=request.form['checker_id'] or None,
    )
    if test.analyst_id and test.analyst_id == test.checker_id:
        flash('Analyst and checker must be different users.')
        return redirect(url_for('main.sample_detail', sample_id=sample_id))
    db.session.add(test)
    db.session.commit()
    flash('Test added')
    return redirect(url_for('main.sample_detail', sample_id=sample_id))


@bp.route('/test/<int:test_id>/update', methods=['POST'])
@login_required
def update_test(test_id):
    test = Test.query.get_or_404(test_id)
    sample = test.sample
    if sample.released:
        flash('Released samples cannot be edited')
        return redirect(url_for('main.sample_detail', sample_id=sample.id))
    old_result = test.result
    test.result = request.form['result']
    test.analyst_id = request.form['analyst_id'] or None
    test.checker_id = request.form['checker_id'] or None
    if test.analyst_id and test.analyst_id == test.checker_id:
        flash('Analyst and checker must differ')
        return redirect(url_for('main.sample_detail', sample_id=sample.id))
    db.session.commit()
    log_change('test', test.id, 'result', old_result, test.result)
    flash('Test updated')
    return redirect(url_for('main.sample_detail', sample_id=sample.id))


@bp.route('/update')
@login_required
def update_app():
    if current_user.role != 'admin':
        flash('Only admin can update the application.')
        return redirect(url_for('main.sample_list'))
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(['git', 'pull'], cwd=repo_dir, capture_output=True, text=True)
    if result.returncode != 0:
        flash('Update failed: ' + result.stderr)
        return redirect(url_for('main.sample_list'))
    flash('Application updated, restarting...')
    os._exit(0)
