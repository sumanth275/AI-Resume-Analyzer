import os
import tempfile
import pytest
from app import create_app
from config import Config

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    upload_dir = tempfile.mkdtemp()
    
    app = create_app(TestConfig)
    app.config['DATABASE_PATH'] = db_path
    app.config['UPLOAD_FOLDER'] = upload_dir

    with app.test_client() as client:
        with app.app_context():
            from database.db import init_db
            init_db(app)
        yield client

    os.close(db_fd)
    os.unlink(db_path)

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"AI Resume Analyzer" in response.data

def test_register_and_login(client):
    # Register
    res = client.post('/auth/register', data={
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Dashboard" in res.data

    # Logout
    res = client.get('/auth/logout', follow_redirects=True)
    assert res.status_code == 200

    # Login
    res = client.post('/auth/login', data={
        'email': 'testuser@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Dashboard" in res.data

def test_stale_session_redirect(client):
    # Set an invalid/nonexistent user_id in session (e.g. after DB reset)
    with client.session_transaction() as sess:
        sess['user_id'] = 99999
        sess['user_name'] = 'Ghost User'

    # Accessing protected route should clear session, flash message, and redirect to login
    res = client.get('/dashboard', follow_redirects=True)
    assert res.status_code == 200
    assert b"Your session is no longer valid. Please log in again." in res.data

    # Verify session user_id was cleared
    with client.session_transaction() as sess:
        assert 'user_id' not in sess
