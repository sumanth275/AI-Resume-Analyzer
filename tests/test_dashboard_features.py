import io
import os
import tempfile
import pymupdf as fitz
import pytest
from app import create_app
from config import Config
from database.db import init_db, get_db
from models.user_model import UserModel
from models.job_portal_model import JobListingModel

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

def create_sample_pdf(text="John Doe\nSoftware Engineer\nSkills: Python, Flask, SQL, Docker, Git, REST APIs, Machine Learning\nExperience: 3 years building web services."):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

@pytest.fixture
def app_and_client():
    db_fd, db_path = tempfile.mkstemp()
    upload_dir = tempfile.mkdtemp()

    app = create_app(TestConfig)
    app.config['DATABASE_PATH'] = db_path
    app.config['UPLOAD_FOLDER'] = upload_dir

    with app.test_client() as client:
        with app.app_context():
            init_db(app)
            # Create a sample user
            user_id = UserModel.create_user(
                name="SaaS Candidate",
                email="candidate@example.com",
                password="password123",
                is_admin=0
            )
            # Create sample job listings
            JobListingModel.create_listing(
                title="Python Backend Developer",
                company="TechCorp Solutions",
                location="San Francisco, CA",
                description="We need a Python developer experienced with Flask, REST APIs, SQL, Docker, and Git.",
                required_skills="Python, Flask, SQL, Docker, Git",
                application_type="internal",
                application_url=None,
                created_by=user_id
            )
            JobListingModel.create_listing(
                title="Frontend React Engineer",
                company="DesignWorks",
                location="Remote",
                description="Looking for React, JavaScript, CSS, HTML frontend specialists.",
                required_skills="React, JavaScript, CSS, HTML",
                application_type="internal",
                application_url=None,
                created_by=user_id
            )

        # Log in the candidate
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_name'] = "SaaS Candidate"
            sess['user_email'] = "candidate@example.com"
            sess['user_role'] = "user"

        yield app, client, user_id

    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)


# FEATURE 1: Dashboard summary cards and statistics
def test_feature_1_dashboard_summary_cards(app_and_client):
    app, client, user_id = app_and_client
    res = client.get('/dashboard')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert "saas-metrics-grid" in html
    assert "Uploaded Resumes" in html
    assert "Match Analyses" in html
    assert "Job Applications" in html
    assert "Avg Job Match Score" in html
    assert "Welcome back" in html


# FEATURE 2: Resume upload and PDF parsing (standalone & scan)
def test_feature_2_resume_upload_and_pdf_parsing(app_and_client):
    app, client, user_id = app_and_client
    pdf_bytes = create_sample_pdf()

    # 1. Standalone vault upload via modal/route
    res = client.post('/resume/upload', data={
        'resume': (io.BytesIO(pdf_bytes), 'my_software_resume.pdf'),
        'next': '/dashboard'
    }, content_type='multipart/form-data', follow_redirects=True)
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert "my_software_resume.pdf" in html

    # Check database parsed text
    with app.app_context():
        db = get_db()
        resume_row = db.execute("SELECT * FROM resumes WHERE user_id = ?", (user_id,)).fetchone()
        assert resume_row is not None
        assert "my_software_resume.pdf" in resume_row['filename']
        assert "Python" in resume_row['resume_text']


# FEATURE 3: Resume match score and skill analysis
def test_feature_3_match_score_and_skills(app_and_client):
    app, client, user_id = app_and_client
    pdf_bytes = create_sample_pdf()

    # Step 1: Upload resume to vault
    client.post('/resume/upload', data={
        'resume': (io.BytesIO(pdf_bytes), 'candidate_resume.pdf'),
        'next': '/dashboard'
    }, content_type='multipart/form-data', follow_redirects=True)

    with app.app_context():
        db = get_db()
        resume_row = db.execute("SELECT id FROM resumes WHERE user_id = ?", (user_id,)).fetchone()
        resume_id = resume_row['id']

    # Baseline State: circular gauge and extracted skills from candidate resume
    res = client.get('/dashboard')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert "circular-score-wrapper" in html
    assert "circular-chart" in html
    assert "ROLE FIT" in html
    assert "Resume Skills Identified" in html
    assert "Python" in html

    # Step 2: Run a targeted analysis against a job description using existing resume
    res_analysis = client.post('/analyze', data={
        'resume_source': 'existing',
        'existing_resume_id': resume_id,
        'job_title': 'Python Backend Developer',
        'job_description': 'Seeking Python engineer with Flask, SQL, Docker, and REST APIs experience.'
    }, follow_redirects=True)
    assert res_analysis.status_code == 200

    # Job Match State: circular gauge shows JOB MATCH and matched skills
    res_dash = client.get('/dashboard')
    dash_html = res_dash.data.decode('utf-8')
    assert "circular-score-wrapper" in dash_html
    assert "JOB MATCH" in dash_html
    assert "Matching Skills" in dash_html


# FEATURE 4: Job recommendations based on uploaded resume
def test_feature_4_job_recommendations(app_and_client):
    app, client, user_id = app_and_client
    pdf_bytes = create_sample_pdf()

    # Upload resume
    client.post('/resume/upload', data={
        'resume': (io.BytesIO(pdf_bytes), 'resume.pdf'),
        'next': '/dashboard'
    }, content_type='multipart/form-data', follow_redirects=True)

    # Check recommendations appear on dashboard
    res = client.get('/dashboard')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert "job-recommendation-card" in html
    assert "Python Backend Developer" in html
    assert "Match" in html

    # Check dedicated recommendations route
    res_rec = client.get('/jobs/recommendations')
    assert res_rec.status_code == 200
    assert b"Python Backend Developer" in res_rec.data


# FEATURE 5: Explore Job Openings and job search
def test_feature_5_explore_jobs_and_search(app_and_client):
    app, client, user_id = app_and_client

    # 1. Browse all jobs
    res = client.get('/jobs/', follow_redirects=True)
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert "Python Backend Developer" in html
    assert "Frontend React Engineer" in html

    # 2. Search query filter
    res_search = client.get('/jobs/?search=Python', follow_redirects=True)
    assert res_search.status_code == 200
    search_html = res_search.data.decode('utf-8')
    assert "Python Backend Developer" in search_html
    assert "Frontend React Engineer" not in search_html


# FEATURE 6: Apply for jobs and My Job Applications
def test_feature_6_apply_and_track_applications(app_and_client):
    app, client, user_id = app_and_client
    pdf_bytes = create_sample_pdf()

    # Upload resume first so application succeeds
    client.post('/resume/upload', data={
        'resume': (io.BytesIO(pdf_bytes), 'apply_resume.pdf'),
        'next': '/dashboard'
    }, content_type='multipart/form-data', follow_redirects=True)

    with app.app_context():
        db = get_db()
        job = db.execute("SELECT id FROM job_listings WHERE title = 'Python Backend Developer'").fetchone()
        resume = db.execute("SELECT id FROM resumes WHERE user_id = ?", (user_id,)).fetchone()
        job_id = job['id']
        resume_id = resume['id']

    # Apply to job
    res_apply = client.post(f'/jobs/{job_id}/apply', data={
        'resume_id': resume_id,
        'cover_letter': 'I am thrilled to apply for the Python Backend Developer position.'
    }, follow_redirects=True)
    assert res_apply.status_code == 200

    # Verify in My Applications
    res_apps = client.get('/jobs/my-applications')
    assert res_apps.status_code == 200
    apps_html = res_apps.data.decode('utf-8')
    assert "Python Backend Developer" in apps_html
    assert "Submitted Applications" in apps_html

    # Verify Dashboard updates recommended job badge to "Applied"
    res_dash = client.get('/dashboard')
    dash_html = res_dash.data.decode('utf-8')
    assert "Applied" in dash_html


# FEATURE 7: Recent resume analyses and report viewing
def test_feature_7_recent_analyses_and_viewing(app_and_client):
    app, client, user_id = app_and_client
    pdf_bytes = create_sample_pdf()

    # Upload and analyze
    client.post('/analyze', data={
        'resume_file': (io.BytesIO(pdf_bytes), 'test_report.pdf'),
        'job_title': 'Cloud Backend Engineer',
        'job_description': 'Experience in Python, Docker, cloud deployment.'
    }, content_type='multipart/form-data', follow_redirects=True)

    with app.app_context():
        db = get_db()
        analysis = db.execute("SELECT id FROM analyses WHERE user_id = ?", (user_id,)).fetchone()
        analysis_id = analysis['id']

    # Verify recent analysis row rendered on dashboard
    res_dash = client.get('/dashboard')
    dash_html = res_dash.data.decode('utf-8')
    assert "Cloud Backend Engineer" in dash_html
    assert f"/result/{analysis_id}" in dash_html or f"/analysis/{analysis_id}" in dash_html

    # View full analysis report
    res_report = client.get(f'/result/{analysis_id}')
    assert res_report.status_code == 200
    report_html = res_report.data.decode('utf-8')
    assert "Cloud Backend Engineer" in report_html

    # View via /analysis alias as well
    res_alias = client.get(f'/analysis/{analysis_id}')
    assert res_alias.status_code == 200


# FEATURE 8: Uploaded resume history and deletion
def test_feature_8_resume_history_and_deletion(app_and_client):
    app, client, user_id = app_and_client
    pdf_bytes = create_sample_pdf()

    client.post('/resume/upload', data={
        'resume': (io.BytesIO(pdf_bytes), 'delete_me.pdf'),
        'next': '/dashboard'
    }, content_type='multipart/form-data', follow_redirects=True)

    with app.app_context():
        db = get_db()
        resume = db.execute("SELECT id FROM resumes WHERE filename LIKE '%delete_me%'").fetchone()
        resume_id = resume['id']

    # Check on dashboard
    res = client.get('/dashboard')
    assert "delete_me.pdf" in res.data.decode('utf-8')

    # Delete resume via route
    res_del = client.post(f'/resume/delete-resume/{resume_id}', follow_redirects=True)
    assert res_del.status_code == 200

    # Check removed from database & dashboard
    with app.app_context():
        db = get_db()
        assert db.execute("SELECT id FROM resumes WHERE id = ?", (resume_id,)).fetchone() is None
    res_after = client.get('/dashboard')
    assert "delete_me.pdf" not in res_after.data.decode('utf-8')


# FEATURE 9: Download PDF analysis report
def test_feature_9_download_pdf_report(app_and_client):
    app, client, user_id = app_and_client
    pdf_bytes = create_sample_pdf()

    client.post('/analyze', data={
        'resume_file': (io.BytesIO(pdf_bytes), 'pdf_download_test.pdf'),
        'job_title': 'Data Systems Engineer',
        'job_description': 'Experience in SQL, Python, ETL systems.'
    }, content_type='multipart/form-data', follow_redirects=True)

    with app.app_context():
        db = get_db()
        analysis = db.execute("SELECT id FROM analyses WHERE user_id = ?", (user_id,)).fetchone()
        analysis_id = analysis['id']

    res_pdf = client.get(f'/download-report/{analysis_id}')
    assert res_pdf.status_code == 200
    assert res_pdf.mimetype == 'application/pdf'
    assert len(res_pdf.data) > 0
    # Check PDF magic header %PDF
    assert res_pdf.data.startswith(b'%PDF')


# FEATURE 10: Sidebar navigation and mobile responsiveness
def test_feature_10_sidebar_and_responsive_markup(app_and_client):
    app, client, user_id = app_and_client
    res = client.get('/dashboard')
    assert res.status_code == 200
    html = res.data.decode('utf-8')

    # Sidebar markup
    assert 'class="app-sidebar"' in html or 'id="appSidebar"' in html
    assert 'id="sidebarOverlay"' in html
    assert 'class="mobile-toggle-btn"' in html
    assert 'toggleSidebar()' in html

    # Essential SaaS navigation links
    assert '/dashboard' in html
    assert '/analyze-page' in html
    assert '/jobs' in html
    assert '/jobs/recommendations' in html
    assert '/jobs/my-applications' in html
    assert '/auth/logout' in html
