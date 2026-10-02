import re
from services.skill_extractor import extract_skills
from services.text_processor import clean_text

ACTION_WORDS = {
    'developed', 'built', 'created', 'implemented', 'designed', 'managed', 'led', 
    'architected', 'optimized', 'increased', 'reduced', 'improved', 'engineered', 
    'automated', 'deployed', 'orchestrated', 'scaled', 'delivered', 'spearheaded'
}

def analyze_resume_structure(resume_text):
    """
    Analyzes raw resume text and calculates an overall Resume Quality Score (0-100%).
    Returns the numerical score along with detailed section feedback.
    """
    if not resume_text or len(resume_text.strip()) == 0:
        return 0.0, {"error": "Empty resume text"}

    text_lower = resume_text.lower()
    score = 0.0
    details = {}

    # 1. Contact Information Detection (20 pts max)
    contact_pts = 0
    has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text))
    has_phone = bool(re.search(r'(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}', resume_text))
    has_link = bool(re.search(r'(linkedin\.com|github\.com|portfolio|\.io|\.com|\.dev)', text_lower))

    if has_email: contact_pts += 8
    if has_phone: contact_pts += 7
    if has_link: contact_pts += 5

    score += contact_pts
    details['contact_info'] = {
        'score': contact_pts,
        'has_email': has_email,
        'has_phone': has_phone,
        'has_link': has_link
    }

    # 2. Key Sections Detection (30 pts max - 5 pts per section)
    sections = {
        'experience': ['experience', 'work history', 'employment', 'internship', 'positions'],
        'education': ['education', 'university', 'college', 'degree', 'bachelor', 'master', 'phd'],
        'skills': ['skills', 'technical skills', 'technologies', 'competencies', 'expertise'],
        'projects': ['projects', 'key projects', 'personal projects', 'portfolio'],
        'certifications': ['certifications', 'certificates', 'courses', 'licenses', 'achievements'],
        'summary': ['summary', 'objective', 'about me', 'profile', 'overview']
    }

    section_pts = 0
    detected_sections = []
    missing_sections = []

    for sec_name, keywords in sections.items():
        found = any(re.search(rf'\b{kw}\b', text_lower) for kw in keywords)
        if found:
            section_pts += 5
            detected_sections.append(sec_name.capitalize())
        else:
            missing_sections.append(sec_name.capitalize())

    score += section_pts
    details['sections'] = {
        'score': section_pts,
        'detected': detected_sections,
        'missing': missing_sections
    }

    # 3. Skills Count & Technical Depth (25 pts max)
    extracted_skills = extract_skills(resume_text)
    skill_count = len(extracted_skills)
    if skill_count >= 15:
        skill_pts = 25
    elif skill_count >= 10:
        skill_pts = 20
    elif skill_count >= 5:
        skill_pts = 15
    elif skill_count >= 1:
        skill_pts = 8
    else:
        skill_pts = 0

    score += skill_pts
    details['skill_depth'] = {
        'score': skill_pts,
        'count': skill_count,
        'skills': extracted_skills
    }

    # 4. Length & Formatting Quality (15 pts max)
    words = resume_text.split()
    word_count = len(words)
    if 250 <= word_count <= 1000:
        length_pts = 15
    elif 150 <= word_count < 250 or 1000 < word_count <= 1500:
        length_pts = 10
    elif word_count > 0:
        length_pts = 5
    else:
        length_pts = 0

    score += length_pts
    details['formatting'] = {
        'score': length_pts,
        'word_count': word_count
    }

    # 5. Action Verbs & Measurable Metrics (10 pts max)
    action_verb_count = sum(1 for word in words if word.lower() in ACTION_WORDS)
    has_metrics = bool(re.search(r'(\d+%\b|\$\d+|\d+\+|\b\d+\s*users\b|\b\d+\s*clients\b)', text_lower))
    
    impact_pts = 0
    if action_verb_count >= 5:
        impact_pts += 5
    elif action_verb_count >= 2:
        impact_pts += 3
        
    if has_metrics:
        impact_pts += 5

    score += impact_pts
    details['impact'] = {
        'score': impact_pts,
        'action_verb_count': action_verb_count,
        'has_metrics': has_metrics
    }

    final_score = round(min(100.0, score), 1)
    return final_score, details
