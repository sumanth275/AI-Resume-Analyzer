import os
import sqlite3
import pytest
from app import create_app
from database.db import get_db, init_db
from models.user_model import UserModel
from models.analysis_model import ResumeModel
from models.job_portal_model import JobListingModel, JobApplicationModel

@pytest.fixture
def app(tmp_path):
    # Set up temporary database for tests
    test_db_path = str(tmp_path / "test_portal.db")
    
    class TestConfig:
        TESTING = True
        SECRET_KEY = 'test-secret-key'
        DATABASE_PATH = test_db_path
        UPLOAD_FOLDER = str(tmp_path / "uploads")
        ALLOWED_EXTENSIONS = {'pdf'}
        WTF_CSRF_ENABLED = False

    app = create_app(TestConfig)
    
    with app.app_context():
        # Insert admin user
        admin_id = UserModel.create_user('Admin User', 'admin@test.com', 'adminpass123', is_admin=1)
        # Insert normal user 1
        user1_id = UserModel.create_user('Normal User', 'user1@test.com', 'userpass123', is_admin=0)
        # Insert normal user 2
        user2_id = UserModel.create_user('Second User', 'user2@test.com', 'userpass123', is_admin=0)
        
        # Insert sample resume for user 1
        resume1_id = ResumeModel.save_resume(
            user1_id,
            'user1_resume.pdf',
            '/fake/path/user1.pdf',
            'Experienced Python, Flask, SQLite, Docker, and REST API software developer.'
        )

        # Insert sample resume for user 2
        resume2_id = ResumeModel.save_resume(
            user2_id,
            'user2_resume.pdf',
            '/fake/path/user2.pdf',
            'Frontend React, TypeScript, and CSS specialist.'
        )

        # Insert sample active job listing
        listing_internal_id = JobListingModel.create_listing(
            title='Backend Python Developer',
            company='Tech Corp',
            location='Remote',
            description='We need a Python and Flask backend engineer with Docker and SQLite experience.',
            required_skills='Python, Flask, Docker, SQLite, REST API',
            application_type='internal',
            application_url=None,
            is_active=1,
            created_by=admin_id
        )

        # Insert sample external job listing
        listing_external_id = JobListingModel.create_listing(
            title='Cloud Architect',
            company='Cloud Services Ltd',
            location='New York, NY',
            description='Senior cloud engineer needed.',
            required_skills='AWS, Kubernetes, Terraform',
            application_type='external',
            application_url='https://careers.cloudservices.com/apply/101',
            is_active=1,
            created_by=admin_id
        )

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_public_jobs_page(client):
    response = client.get('/jobs/')
    assert response.status_code == 200
    assert b'Backend Python Developer' in response.data
    assert b'Cloud Architect' in response.data


def test_public_jobs_search_filter(client):
    response = client.get('/jobs/?search=Python')
    assert response.status_code == 200
    assert b'Backend Python Developer' in response.data
    assert b'Cloud Architect' not in response.data


def test_admin_portal_unauthorized_access(client):
    # 1. Guest user cannot access admin
    response = client.get('/jobs/admin', follow_redirects=True)
    assert b'Please log in' in response.data

    # 2. Regular user cannot access admin
    client.post('/auth/login', data={'email': 'user1@test.com', 'password': 'userpass123'})
    response = client.get('/jobs/admin', follow_redirects=True)
    assert b'Access denied. Administrator privileges required.' in response.data


def test_admin_portal_authorized_access(client):
    # Admin user can access admin dashboard
    client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'adminpass123'})
    response = client.get('/jobs/admin')
    assert response.status_code == 200
    assert b'Job Listings Management' in response.data
    assert b'Backend Python Developer' in response.data


def test_admin_create_listing_validation(client):
    client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'adminpass123'})
    
    # External job requires valid URL
    response = client.post('/jobs/admin/create', data={
        'title': 'Frontend Developer',
        'company': 'Web Studio',
        'location': 'Austin, TX',
        'description': 'React and Vue developer needed.',
        'required_skills': 'React, Vue',
        'application_type': 'external',
        'application_url': 'invalid-url-format',
        'is_active': '1'
    }, follow_redirects=True)
    assert b'Please provide a valid HTTP/HTTPS URL' in response.data

    # Valid external job succeeds
    response = client.post('/jobs/admin/create', data={
        'title': 'Frontend Developer',
        'company': 'Web Studio',
        'location': 'Austin, TX',
        'description': 'React and Vue developer needed.',
        'required_skills': 'React, Vue',
        'application_type': 'external',
        'application_url': 'https://careers.webstudio.com/jobs/42',
        'is_active': '1'
    }, follow_redirects=True)
    assert b'created successfully' in response.data
    assert b'Frontend Developer' in response.data


def test_internal_job_application_flow(client):
    # Log in as user1
    client.post('/auth/login', data={'email': 'user1@test.com', 'password': 'userpass123'})

    # Get listing details
    response = client.get('/jobs/1')
    assert response.status_code == 200
    assert b'Backend Python Developer' in response.data
    assert b'user1_resume.pdf' in response.data

    # Submit application
    response = client.post('/jobs/1/apply', data={
        'resume_id': '1',
        'cover_letter': 'Excited about this Python role!'
    }, follow_redirects=True)
    assert b'successfully submitted' in response.data

    # Verify application appears in My Applications
    response = client.get('/jobs/my-applications')
    assert response.status_code == 200
    assert b'Backend Python Developer' in response.data
    assert b'Tech Corp' in response.data
    assert b'Pending' in response.data

    # Test duplicate application prevention
    dup_response = client.post('/jobs/1/apply', data={
        'resume_id': '1',
        'cover_letter': 'Second attempt'
    }, follow_redirects=True)
    assert b'already submitted an application' in dup_response.data


def test_unauthorized_resume_application_blocked(client):
    # User 1 attempts to apply using User 2's resume (id=2)
    client.post('/auth/login', data={'email': 'user1@test.com', 'password': 'userpass123'})
    
    response = client.post('/jobs/1/apply', data={
        'resume_id': '2',
        'cover_letter': 'Trying to use someone else resume'
    }, follow_redirects=True)
    assert b'Unauthorized or invalid resume' in response.data


def test_external_job_redirect(client):
    response = client.get('/jobs/2/apply-external')
    assert response.status_code == 302
    assert response.headers['Location'] == 'https://careers.cloudservices.com/apply/101'


def test_job_recommendations_flow(client):
    # Log in as user 1 (Python skills)
    client.post('/auth/login', data={'email': 'user1@test.com', 'password': 'userpass123'})
    
    response = client.get('/jobs/recommendations')
    assert response.status_code == 200
    assert b'AI Job Recommendations' in response.data
    assert b'Backend Python Developer' in response.data
    assert b'Python' in response.data


def test_admin_toggle_and_delete_listing(client):
    client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'adminpass123'})
    
    # Toggle inactive (follow redirect to consume flash message on admin page)
    toggle_res = client.post('/jobs/admin/toggle/1', follow_redirects=True)
    assert b'deactivated' in toggle_res.data
    with client.application.app_context():
        job = JobListingModel.get_by_id(1)
        assert job['is_active'] == 0

    # Inactive job should not appear on public list
    pub_response = client.get('/jobs/')
    assert b'Backend Python Developer' not in pub_response.data

    # Toggle back to active
    client.post('/jobs/admin/toggle/1', follow_redirects=True)
    with client.application.app_context():
        job = JobListingModel.get_by_id(1)
        assert job['is_active'] == 1

    # Now it appears again
    pub_active_response = client.get('/jobs/')
    assert b'Backend Python Developer' in pub_active_response.data

    # Delete listing
    client.post('/jobs/admin/delete/1', follow_redirects=True)
    with client.application.app_context():
        job = JobListingModel.get_by_id(1)
        assert job is None
