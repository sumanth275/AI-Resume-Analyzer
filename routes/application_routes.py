from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    current_app,
)
from models.resume_model import ResumeModel
from models.application_model import JobApplicationModel
from services.auto_apply_engine import preview_auto_apply, execute_auto_apply
from utils.helpers import login_required

application_bp = Blueprint('applications', __name__)


@application_bp.route('/applications', methods=['GET'])
@login_required
def list_applications():
    user_id = session['user_id']
    status_filter = request.args.get('status', 'all').strip().lower()
    applications = JobApplicationModel.get_user_applications(user_id, status_filter=status_filter)
    stats = JobApplicationModel.get_application_stats(user_id)
    return render_template(
        'applications.html',
        applications=applications,
        stats=stats,
        status_filter=status_filter,
    )


@application_bp.route('/applications/<int:application_id>/withdraw', methods=['POST'])
@login_required
def withdraw_application(application_id):
    user_id = session['user_id']
    withdrawn = JobApplicationModel.withdraw_application(application_id, user_id)
    if withdrawn:
        flash('Pending application withdrawn successfully.', 'info')
    else:
        flash('Only pending applications belonging to your account can be withdrawn.', 'warning')
    return redirect(url_for('applications.list_applications'))


@application_bp.route('/auto-apply', methods=['GET'])
@login_required
def auto_apply_page():
    user_id = session['user_id']
    user_resumes = ResumeModel.get_by_user(user_id)

    if not user_resumes:
        flash('Please upload a resume first before configuring Auto-Apply.', 'info')
        return redirect(url_for('analysis.upload_page'))

    selected_resume_id = request.args.get('resume_id', type=int) or user_resumes[0]['id']
    default_threshold = current_app.config.get('AUTO_APPLY_DEFAULT_THRESHOLD', 60.0)
    min_match_score = request.args.get('min_match_score', default=default_threshold, type=float)
    max_applications = request.args.get('max_applications', default=5, type=int)
    location_filter = request.args.get('location', default='', type=str).strip()

    try:
        preview = preview_auto_apply(
            user_id=user_id,
            resume_id=selected_resume_id,
            min_match_score=min_match_score,
            location=location_filter or None,
            max_applications=max_applications,
        )
    except ValueError:
        selected_resume_id = user_resumes[0]['id']
        preview = preview_auto_apply(
            user_id=user_id,
            resume_id=selected_resume_id,
            min_match_score=min_match_score,
            location=location_filter or None,
            max_applications=max_applications,
        )

    history = JobApplicationModel.get_auto_apply_history(user_id, limit=8)

    return render_template(
        'auto_apply.html',
        user_resumes=user_resumes,
        selected_resume_id=selected_resume_id,
        min_match_score=preview['min_match_score'],
        max_applications=preview['max_applications'],
        location_filter=location_filter,
        preview=preview,
        history=history,
    )


@application_bp.route('/auto-apply/preview', methods=['POST'])
@login_required
def preview_auto_apply_api():
    user_id = session['user_id']
    payload = request.get_json(silent=True) or request.form

    resume_id = int(payload.get('resume_id', 0))
    min_match_score = float(payload.get('min_match_score', 60.0))
    max_applications = int(payload.get('max_applications', 5))
    location = (payload.get('location') or '').strip() or None

    try:
        preview = preview_auto_apply(
            user_id=user_id,
            resume_id=resume_id,
            min_match_score=min_match_score,
            location=location,
            max_applications=max_applications,
        )
        return jsonify({
            'success': True,
            'total_evaluated': preview['total_evaluated'],
            'total_eligible_count': preview['total_eligible_count'],
            'eligible_jobs': preview['eligible_jobs'],
            'already_applied_count': len(preview['already_applied']),
            'below_threshold_count': len(preview['below_threshold']),
            'external_jobs_count': len(preview['external_jobs']),
        })
    except ValueError as exc:
        return jsonify({'success': False, 'message': str(exc)}), 400


@application_bp.route('/auto-apply/run', methods=['POST'])
@login_required
def run_auto_apply():
    user_id = session['user_id']
    resume_id = request.form.get('resume_id', type=int)
    min_match_score = request.form.get('min_match_score', default=60.0, type=float)
    max_applications = request.form.get('max_applications', default=5, type=int)
    location_filter = request.form.get('location', default='', type=str).strip()
    custom_cover_letter = request.form.get('custom_cover_letter', default='', type=str).strip() or None

    selected_job_ids_raw = request.form.getlist('selected_job_ids')
    selected_job_ids = [int(jid) for jid in selected_job_ids_raw if jid.isdigit()] if selected_job_ids_raw else None

    if not resume_id:
        flash('Please select a resume before running Auto-Apply.', 'danger')
        return redirect(url_for('applications.auto_apply_page'))

    try:
        result = execute_auto_apply(
            user_id=user_id,
            resume_id=resume_id,
            min_match_score=min_match_score,
            location=location_filter or None,
            max_applications=max_applications,
            selected_job_ids=selected_job_ids,
            custom_cover_letter=custom_cover_letter,
        )
    except ValueError as exc:
        flash(str(exc), 'danger')
        return redirect(url_for('applications.auto_apply_page'))

    if result['applied_count'] > 0:
        flash(
            f"Auto-Apply submitted {result['applied_count']} application(s) successfully!",
            'success',
        )
        return redirect(url_for('applications.list_applications'))

    flash(
        'No eligible internal jobs matched your threshold or all matching jobs were already applied to.',
        'warning',
    )
    return redirect(
        url_for(
            'applications.auto_apply_page',
            resume_id=resume_id,
            min_match_score=min_match_score,
            max_applications=max_applications,
            location=location_filter,
        )
    )
