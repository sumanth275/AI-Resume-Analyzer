from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort
)
from models.job_portal_model import JobListingModel, JobApplicationModel
from models.analysis_model import ResumeModel
from utils.helpers import login_required, admin_required
from utils.validators import validate_url

job_bp = Blueprint('jobs', __name__)


# =========================================================================
# PUBLIC JOB LISTINGS & RECOMMENDATIONS
# =========================================================================

@job_bp.route('/', methods=['GET'])
def public_jobs():
    search = request.args.get('search', '').strip()
    location = request.args.get('location', '').strip()

    listings = JobListingModel.get_active_listings(search=search, location=location)

    recommendations = []
    applied_ids = set()

    if 'user_id' in session:
        user_id = session['user_id']
        user_resumes = ResumeModel.get_by_user(user_id)
        if user_resumes:
            # Use most recent resume for quick recommendations
            latest_resume = user_resumes[0]
            recommendations = JobListingModel.get_recommended_listings(
                resume_text=latest_resume['resume_text'],
                limit=3
            )

        user_apps = JobApplicationModel.get_user_applications(user_id)
        applied_ids = {app['job_listing_id'] for app in user_apps}

    return render_template(
        'jobs/job_list.html',
        listings=listings,
        recommendations=recommendations,
        search=search,
        location=location,
        applied_ids=applied_ids
    )


@job_bp.route('/<int:listing_id>', methods=['GET'])
def job_detail(listing_id):
    listing = JobListingModel.get_by_id(listing_id)
    if not listing:
        flash('Job listing not found.', 'danger')
        return redirect(url_for('jobs.public_jobs'))

    # If listing is inactive, only admin can view it
    if not listing['is_active'] and not session.get('is_admin'):
        flash('This job listing is currently inactive.', 'warning')
        return redirect(url_for('jobs.public_jobs'))

    user_application = None
    user_resumes = []
    skills_list = []

    if listing['required_skills']:
        skills_list = [s.strip() for s in listing['required_skills'].split(',') if s.strip()]

    if 'user_id' in session:
        user_id = session['user_id']
        user_application = JobApplicationModel.has_user_applied(listing_id, user_id)
        user_resumes = ResumeModel.get_by_user(user_id)

    return render_template(
        'jobs/job_detail.html',
        listing=listing,
        user_application=user_application,
        user_resumes=user_resumes,
        skills_list=skills_list
    )


@job_bp.route('/recommendations', methods=['GET'])
@login_required
def recommendations():
    user_id = session['user_id']
    user_resumes = ResumeModel.get_by_user(user_id)

    if not user_resumes:
        flash('Please upload a resume first to receive personalized job recommendations.', 'info')
        return redirect(url_for('analysis.upload_page'))

    selected_resume_id = request.args.get('resume_id', type=int)
    selected_resume = None

    if selected_resume_id:
        selected_resume = ResumeModel.get_by_id(selected_resume_id, user_id)

    if not selected_resume:
        selected_resume = user_resumes[0]

    recommended_jobs = JobListingModel.get_recommended_listings(
        resume_text=selected_resume['resume_text'],
        limit=10
    )

    user_apps = JobApplicationModel.get_user_applications(user_id)
    applied_ids = {app['job_listing_id'] for app in user_apps}

    return render_template(
        'jobs/recommendations.html',
        recommendations=recommended_jobs,
        user_resumes=user_resumes,
        selected_resume=selected_resume,
        applied_ids=applied_ids
    )


# =========================================================================
# APPLICATION SUBMISSIONS & CANDIDATE TRACKER
# =========================================================================

@job_bp.route('/<int:listing_id>/apply', methods=['POST'])
@login_required
def apply_job(listing_id):
    user_id = session['user_id']
    listing = JobListingModel.get_by_id(listing_id)

    if not listing or not listing['is_active']:
        flash('This job listing is no longer accepting applications.', 'danger')
        return redirect(url_for('jobs.public_jobs'))

    if listing['application_type'] == 'external':
        flash('This position requires an external application. Please follow the official link.', 'warning')
        return redirect(url_for('jobs.job_detail', listing_id=listing_id))

    # Check for duplicate application
    existing_app = JobApplicationModel.has_user_applied(listing_id, user_id)
    if existing_app:
        flash('You have already submitted an application for this job listing.', 'warning')
        return redirect(url_for('jobs.my_applications'))

    resume_id = request.form.get('resume_id', type=int)
    cover_letter = request.form.get('cover_letter', '').strip()

    if not resume_id:
        flash('Please select one of your uploaded resumes to apply.', 'danger')
        return redirect(url_for('jobs.job_detail', listing_id=listing_id))

    # Verify that the resume belongs to the logged-in user
    resume = ResumeModel.get_by_id(resume_id, user_id)
    if not resume:
        flash('Unauthorized or invalid resume selected.', 'danger')
        return redirect(url_for('jobs.job_detail', listing_id=listing_id))

    try:
        JobApplicationModel.apply_internal(
            job_listing_id=listing_id,
            user_id=user_id,
            resume_id=resume_id,
            cover_letter=cover_letter
        )
        flash(f'Your application for "{listing["title"]}" at {listing["company"]} was successfully submitted!', 'success')
        return redirect(url_for('jobs.my_applications'))
    except Exception as e:
        flash(f'An error occurred while submitting your application: {str(e)}', 'danger')
        return redirect(url_for('jobs.job_detail', listing_id=listing_id))


@job_bp.route('/<int:listing_id>/apply-external', methods=['GET'])
def apply_external(listing_id):
    listing = JobListingModel.get_by_id(listing_id)
    if not listing:
        flash('Job listing not found.', 'danger')
        return redirect(url_for('jobs.public_jobs'))

    url = listing['application_url']
    if not url or not validate_url(url):
        flash('The external application URL for this job listing is invalid or missing.', 'danger')
        return redirect(url_for('jobs.job_detail', listing_id=listing_id))

    return redirect(url)


@job_bp.route('/my-applications', methods=['GET'])
@login_required
def my_applications():
    user_id = session['user_id']
    applications = JobApplicationModel.get_user_applications(user_id)
    return render_template('jobs/my_applications.html', applications=applications)


# =========================================================================
# ADMIN-ONLY JOB MANAGEMENT
# =========================================================================

@job_bp.route('/admin', methods=['GET'])
@admin_required
def admin_dashboard():
    listings = JobListingModel.get_all_listings()
    return render_template('jobs/admin_listings.html', listings=listings)


@job_bp.route('/admin/create', methods=['GET', 'POST'])
@admin_required
def admin_create_listing():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip()
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        required_skills = request.form.get('required_skills', '').strip()
        application_type = request.form.get('application_type', 'internal').strip()
        application_url = request.form.get('application_url', '').strip()
        is_active = 1 if request.form.get('is_active') == '1' else 0

        # Validations
        if not title or not company or not description:
            flash('Title, company, and job description are required.', 'danger')
            return render_template(
                'jobs/admin_form.html',
                action='create',
                form_data=request.form
            )

        if application_type not in ('internal', 'external'):
            flash('Application type must be either internal or external.', 'danger')
            return render_template(
                'jobs/admin_form.html',
                action='create',
                form_data=request.form
            )

        if application_type == 'external':
            if not application_url or not validate_url(application_url):
                flash('Please provide a valid HTTP/HTTPS URL for external applications.', 'danger')
                return render_template(
                    'jobs/admin_form.html',
                    action='create',
                    form_data=request.form
                )

        try:
            listing_id = JobListingModel.create_listing(
                title=title,
                company=company,
                location=location,
                description=description,
                required_skills=required_skills,
                application_type=application_type,
                application_url=application_url if application_type == 'external' else None,
                is_active=is_active,
                created_by=session['user_id']
            )
            flash(f'Job listing "{title}" created successfully!', 'success')
            return redirect(url_for('jobs.admin_dashboard'))
        except Exception as e:
            flash(f'Failed to create job listing: {str(e)}', 'danger')
            return render_template(
                'jobs/admin_form.html',
                action='create',
                form_data=request.form
            )

    return render_template('jobs/admin_form.html', action='create', form_data={})


@job_bp.route('/admin/edit/<int:listing_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_listing(listing_id):
    listing = JobListingModel.get_by_id(listing_id)
    if not listing:
        flash('Job listing not found.', 'danger')
        return redirect(url_for('jobs.admin_dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip()
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        required_skills = request.form.get('required_skills', '').strip()
        application_type = request.form.get('application_type', 'internal').strip()
        application_url = request.form.get('application_url', '').strip()
        is_active = 1 if request.form.get('is_active') == '1' else 0

        if not title or not company or not description:
            flash('Title, company, and job description are required.', 'danger')
            return render_template(
                'jobs/admin_form.html',
                action='edit',
                listing=listing,
                form_data=request.form
            )

        if application_type not in ('internal', 'external'):
            flash('Application type must be either internal or external.', 'danger')
            return render_template(
                'jobs/admin_form.html',
                action='edit',
                listing=listing,
                form_data=request.form
            )

        if application_type == 'external':
            if not application_url or not validate_url(application_url):
                flash('Please provide a valid HTTP/HTTPS URL for external applications.', 'danger')
                return render_template(
                    'jobs/admin_form.html',
                    action='edit',
                    listing=listing,
                    form_data=request.form
                )

        try:
            JobListingModel.update_listing(
                listing_id=listing_id,
                title=title,
                company=company,
                location=location,
                description=description,
                required_skills=required_skills,
                application_type=application_type,
                application_url=application_url if application_type == 'external' else None,
                is_active=is_active
            )
            flash(f'Job listing "{title}" updated successfully!', 'success')
            return redirect(url_for('jobs.admin_dashboard'))
        except Exception as e:
            flash(f'Failed to update job listing: {str(e)}', 'danger')

    return render_template('jobs/admin_form.html', action='edit', listing=listing, form_data=dict(listing))


@job_bp.route('/admin/toggle/<int:listing_id>', methods=['POST'])
@admin_required
def admin_toggle_listing(listing_id):
    listing = JobListingModel.get_by_id(listing_id)
    if not listing:
        flash('Job listing not found.', 'danger')
    else:
        JobListingModel.toggle_status(listing_id)
        new_status = 'deactivated' if listing['is_active'] else 'activated'
        flash(f'Job listing "{listing["title"]}" {new_status}.', 'info')
    return redirect(url_for('jobs.admin_dashboard'))


@job_bp.route('/admin/delete/<int:listing_id>', methods=['POST'])
@admin_required
def admin_delete_listing(listing_id):
    listing = JobListingModel.get_by_id(listing_id)
    if not listing:
        flash('Job listing not found.', 'danger')
    else:
        JobListingModel.delete_listing(listing_id)
        flash(f'Job listing "{listing["title"]}" and its applications deleted.', 'info')
    return redirect(url_for('jobs.admin_dashboard'))


@job_bp.route('/admin/applications/<int:listing_id>', methods=['GET'])
@admin_required
def admin_view_applications(listing_id):
    listing = JobListingModel.get_by_id(listing_id)
    if not listing:
        flash('Job listing not found.', 'danger')
        return redirect(url_for('jobs.admin_dashboard'))

    applications = JobApplicationModel.get_applications_by_listing(listing_id)
    return render_template(
        'jobs/admin_applications.html',
        listing=listing,
        applications=applications
    )


@job_bp.route('/admin/application-status/<int:application_id>', methods=['POST'])
@admin_required
def admin_update_application_status(application_id):
    new_status = request.form.get('status', '').strip().lower()
    listing_id = request.form.get('listing_id', type=int)

    valid_statuses = ('pending', 'reviewed', 'shortlisted', 'accepted', 'rejected')
    if new_status in valid_statuses:
        JobApplicationModel.update_status(application_id, new_status)
        flash(f'Application status updated to "{new_status.title()}".', 'success')
    else:
        flash('Invalid status provided.', 'danger')

    if listing_id:
        return redirect(url_for('jobs.admin_view_applications', listing_id=listing_id))
    return redirect(url_for('jobs.admin_dashboard'))
