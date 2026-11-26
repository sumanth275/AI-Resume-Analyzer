import pytest
from app import create_app
from config import Config
from database.db import init_db, seed_default_jobs_if_needed
from models.user_model import UserModel
from models.analysis_model import ResumeModel
from models.job_portal_model import JobListingModel, JobApplicationModel
from services.job_matcher import (
    calculate_multiple_job_matches,
    get_strongest_skill_and_recommendation
)

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

@pytest.fixture
def portal_client(tmp_path):
    test_db = str(tmp_path / "flow_test.db")
    upload_dir = str(tmp_path / "uploads")

    app = create_app(TestConfig)
    app.config['DATABASE_PATH'] = test_db
    app.config['UPLOAD_FOLDER'] = upload_dir

    with app.app_context():
        init_db(app)
        seed_default_jobs_if_needed(app)

        # User
        user_id = UserModel.create_user("Workflow User", "flow@example.com", "pass123")

        # Resume with strong Python skills
        resume_id = ResumeModel.save_resume(
            user_id,
            "python_dev_resume.pdf",
            "/fake/python_dev.pdf",
            "Experienced Python, Flask, Django, SQL, PostgreSQL, REST API, Git, Docker, and Linux developer."
        )

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_name'] = "Workflow User"
            sess['user_email'] = "flow@example.com"
        yield client, user_id, resume_id, app

def test_workflow_requirement_strongest_skill_and_roles(portal_client):
    client, user_id, resume_id, app = portal_client

    with app.app_context():
        resume = ResumeModel.get_by_id(resume_id, user_id)
        strongest_info = get_strongest_skill_and_recommendation(resume['resume_text'])

        # 1. Identified strongest skill
        assert strongest_info['strongest_skill'] is not None
        assert strongest_info['strongest_skill'] in ["Python", "SQL", "Flask", "Django"]

        # 2. Recommended role dependent upon strongest skill
        assert strongest_info['recommended_role'] is not None
        assert strongest_info['match_percentage'] > 0

        # 3. 20 Predefined roles matching
        all_roles = calculate_multiple_job_matches(resume['resume_text'])
        assert len(all_roles) == 20
        for r in all_roles:
            assert 'technical_skills_match_percentage' in r
            assert 'matching_skills' in r
            assert 'missing_skills' in r

def test_workflow_requirement_recommend_at_least_20_jobs_and_apply(portal_client):
    client, user_id, resume_id, app = portal_client

    # Check recommendations page
    res = client.get('/jobs/recommendations')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert "Recommended Openings" in html

    with app.app_context():
        resume = ResumeModel.get_by_id(resume_id, user_id)
        recommended_jobs = JobListingModel.get_recommended_listings(resume_text=resume['resume_text'], limit=25)
        assert len(recommended_jobs) >= 20
        top_job = recommended_jobs[0]
        top_job_id = top_job['id']
        top_job_title = top_job['title']

        # Check matching and missing skills are populated for every job
        for job in recommended_jobs:
            assert 'matching_skills' in job
            assert 'missing_skills' in job
            assert 'match_score' in job

    # Apply for the top recommended job (outside app_context)
    apply_res = client.post(f"/jobs/{top_job_id}/apply", data={
        'resume_id': resume_id,
        'cover_letter': 'Excited to apply for this position matching my skills!'
    }, follow_redirects=True)
    assert apply_res.status_code == 200
    assert b"successfully submitted" in apply_res.data

    # Verify application in my-applications
    apps_res = client.get('/jobs/my-applications')
    assert apps_res.status_code == 200
    assert top_job_title.encode('utf-8') in apps_res.data


def test_bangalore_and_hyderabad_job_suggestions(portal_client):
    client, user_id, resume_id, app = portal_client

    with app.app_context():
        resume = ResumeModel.get_by_id(resume_id, user_id)
        recommended_jobs = JobListingModel.get_recommended_listings(resume_text=resume['resume_text'], limit=30)

        # Verify Bangalore and Hyderabad jobs exist in seeded recommendations
        blr_jobs = [j for j in recommended_jobs if any(k in (j.get('location') or '').lower() for k in ['bangalore', 'bengaluru'])]
        hyd_jobs = [j for j in recommended_jobs if 'hyderabad' in (j.get('location') or '').lower()]

        assert len(blr_jobs) >= 5, f"Expected at least 5 Bangalore jobs, got {len(blr_jobs)}"
        assert len(hyd_jobs) >= 5, f"Expected at least 5 Hyderabad jobs, got {len(hyd_jobs)}"

    # Test route filtering for Bangalore
    blr_res = client.get('/jobs/recommendations?location=bangalore')
    assert blr_res.status_code == 200
    blr_html = blr_res.data.decode('utf-8')
    assert "Bangalore" in blr_html or "Bengaluru" in blr_html

    # Test route filtering for Hyderabad
    hyd_res = client.get('/jobs/recommendations?location=hyderabad')
    assert hyd_res.status_code == 200
    hyd_html = hyd_res.data.decode('utf-8')
    assert "Hyderabad" in hyd_html


def test_customized_resume_data_analysis_output(portal_client):
    from services.resume_analyzer import get_customized_resume_analysis

    sample_resume = """
    Jane Doe | jane.doe@example.com | (555) 123-4567 | github.com/janedoe
    EXPERIENCE
    Senior Software Engineer at TechCorp (2020 - Present)
    - Engineered scalable microservices using Python, Django, Docker, and PostgreSQL.
    - Optimized database queries, reducing response times by 40% for 100000+ users.
    - Led a team of 5 engineers to deliver Cloud REST APIs on AWS.
    SKILLS
    Python, Java, Flask, Django, SQL, PostgreSQL, Redis, Docker, Kubernetes, AWS, Git, CI/CD
    EDUCATION
    B.S. in Computer Science
    """

    analysis = get_customized_resume_analysis(sample_resume)

    # 1. Total skills and taxonomy
    assert analysis["total_skills_count"] >= 8
    cat_skills = analysis["categorized_skills"]
    assert "Programming Languages" in cat_skills
    assert "Python" in cat_skills["Programming Languages"]
    assert "Web & Backend Frameworks" in cat_skills
    assert "Databases & Cloud Infrastructure" in cat_skills

    # 2. Quantitative metrics
    metrics = analysis["quantitative_metrics"]
    assert metrics["word_count"] > 30
    assert metrics["action_verb_count"] >= 2
    assert "Engineered" in metrics["detected_action_verbs"] or "Optimized" in metrics["detected_action_verbs"] or "Led" in metrics["detected_action_verbs"]
    assert len(metrics["detected_metrics"]) > 0
    assert any("40%" in m for m in metrics["detected_metrics"])

    # 3. Contact information
    contact = analysis["contact_info"]
    assert contact["email"] == "jane.doe@example.com"
    assert "555" in contact["phone"]
    assert len(contact["links"]) > 0


def test_result_page_renders_bangalore_hyderabad_and_custom_analysis(portal_client):
    from models.analysis_model import AnalysisModel, JobModel
    client, user_id, resume_id, app = portal_client

    resume_text = "Experienced Python developer with Flask, SQL, Docker, and REST API skills. 5+ years building backend systems."

    with app.app_context():
        job_id = JobModel.save_job(user_id, "Python Developer", "Looking for Python, Flask, SQL, Docker developers")
        analysis_id = AnalysisModel.save_analysis(
            user_id=user_id,
            resume_id=resume_id,
            job_id=job_id,
            match_score=85.0,
            resume_score=80.0,
            skills_match_score=90.0,
            keyword_match_score=85.0,
            matching_skills=["Python", "Flask", "SQL", "Docker"],
            missing_skills=["Kubernetes"],
            recommendations=["Learn Kubernetes for container orchestration"]
        )

    res = client.get(f"/result/{analysis_id}")
    assert res.status_code == 200
    html = res.data.decode('utf-8')

    # Verify Bangalore & Hyderabad Openings section
    assert "RECOMMENDED JOBS NEAR BANGALORE & HYDERABAD" in html
    assert "Bangalore / Bengaluru" in html
    assert "Hyderabad" in html

    # Verify Customized Resume Data Analysis & Clear Output section
    assert "CUSTOMIZED RESUME DATA ANALYSIS & CLEAR OUTPUT" in html
    assert "Categorized Skills Matrix" in html
    assert "Quantitative & ATS Metrics" in html
    assert "Clear JSON Output" in html
    assert "raw-analysis-json" in html
