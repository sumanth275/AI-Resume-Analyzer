from services.text_processor import clean_text, preprocess_text
from services.skill_extractor import extract_skills
from services.resume_analyzer import analyze_resume_structure
from services.job_matcher import (
    calculate_job_match,
    calculate_multiple_job_matches,
    get_career_recommendation,
    generate_career_recommendation
)

def test_clean_text():
    raw = "Check out https://github.com/test or contact john@test.com! Skills: C++, Python & React.js."
    cleaned = clean_text(raw)
    assert "https" not in cleaned
    assert "john@test.com" not in cleaned
    assert "c++" in cleaned
    assert "python" in cleaned

def test_extract_skills():
    text = "Experienced Senior Python Engineer skilled in Flask, SQL, Docker, React.js, and AWS."
    skills = extract_skills(text)
    assert "Python" in skills
    assert "Flask" in skills
    assert "SQL" in skills
    assert "Docker" in skills
    assert "React" in skills or "React.js" in skills
    assert "AWS" in skills

def test_analyze_resume_structure():
    resume = """
    Jane Smith
    Email: jane@example.com | Phone: 123-456-7890 | LinkedIn: linkedin.com/in/janesmith
    
    SUMMARY
    Experienced Software Engineer with 5+ years of experience in full-stack web development.

    EXPERIENCE
    Senior Developer at Tech Corp
    - Developed scalable REST APIs using Flask and Python, improving performance by 40%.
    - Built web interfaces with React and Tailwind CSS.

    EDUCATION
    Bachelor of Science in Computer Science - State University

    SKILLS
    Python, Flask, SQL, Docker, Git, CI/CD

    PROJECTS
    AI Resume Analyzer - Built full-stack web app for matching candidate profiles.
    """
    score, details = analyze_resume_structure(resume)
    assert score >= 70.0
    assert details['contact_info']['has_email'] is True
    assert details['contact_info']['has_phone'] is True
    assert details['impact']['has_metrics'] is True

def test_calculate_job_match():
    resume = "Python Developer experienced in Flask, SQL, Machine Learning, Git."
    job_desc = "Looking for a Python Developer with Flask, SQL, Machine Learning, Git, Docker, and AWS experience."
    
    result = calculate_job_match(resume, job_desc)
    assert result['match_score'] > 50.0
    assert "Python" in result['matching_skills']
    assert "Flask" in result['matching_skills']
    assert "Docker" in result['missing_skills']
    assert "AWS" in result['missing_skills']
    assert len(result['recommendations']) > 0

def test_career_recommendation():
    resume = "Senior Python Developer experienced in Flask, SQL, Machine Learning, Git, PostgreSQL, Pandas."
    
    raw_role_results = calculate_multiple_job_matches(resume)
    assert len(raw_role_results) >= 5
    
    rec = get_career_recommendation(resume, raw_role_results)
    
    # 1. Top 5 job recommendations returned
    assert len(rec['top_jobs']) == 5
    
    # 2. Results sorted by match_score descending
    scores = [j['match_score'] for j in rec['top_jobs']]
    assert scores == sorted(scores, reverse=True)
    
    # 3. Best job is the first result
    assert rec['best_job'] is not None
    assert rec['best_job']['job_role'] == rec['top_jobs'][0]['job_role']
    assert rec['best_job']['match_score'] == rec['top_jobs'][0]['match_score']
    
    # 4. Missing skills returned
    assert isinstance(rec['skill_gap']['missing'], list)
    assert isinstance(rec['skill_gap']['matching'], list)
    assert isinstance(rec['skill_gap']['to_learn'], list)
    
    # 5. Career recommendation does not modify existing score
    for top_job in rec['top_jobs']:
        matching_raw = next(r for r in raw_role_results if r['job_role'] == top_job['job_role'])
        assert top_job['match_score'] == matching_raw['match_score']
        
    # 6. Roadmap and Next Best Action properly structured
    assert len(rec['roadmap']) == 4
    assert rec['next_best_action'] is not None
    assert rec['next_best_action']['job_title'] == rec['best_job']['job_role']
    assert rec['next_best_action']['match_score'] == rec['best_job']['match_score']
