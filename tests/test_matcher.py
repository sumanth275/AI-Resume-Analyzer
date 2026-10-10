from services.text_processor import clean_text, preprocess_text
from services.skill_extractor import extract_skills
from services.resume_analyzer import analyze_resume_structure
from services.job_matcher import calculate_job_match, calculate_multiple_job_matches

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

def test_calculate_multiple_job_matches():
    resume = "Python Developer experienced in Flask, Django, SQL, Git, REST API, HTML, CSS, JavaScript."
    results = calculate_multiple_job_matches(resume)

    assert len(results) == 20

    for role in results:
        assert 'technical_skills_match_percentage' in role
        assert 'keyword_match_score' in role
        assert 'match_score' in role
        assert 'matching_skills' in role
        assert 'missing_skills' in role

        total_skills = len(role['matching_skills']) + len(role['missing_skills'])
        if total_skills > 0:
            expected_pct = round((len(role['matching_skills']) / total_skills) * 100, 1)
            assert role['technical_skills_match_percentage'] == expected_pct

    # Verify primary ranking by technical_skills_match_percentage and secondary ranking by keyword_match_score
    for i in range(len(results) - 1):
        curr = results[i]
        nxt = results[i + 1]
        if curr['technical_skills_match_percentage'] == nxt['technical_skills_match_percentage']:
            assert curr['keyword_match_score'] >= nxt['keyword_match_score']
        else:
            assert curr['technical_skills_match_percentage'] > nxt['technical_skills_match_percentage']
