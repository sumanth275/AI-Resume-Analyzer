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


SKILL_CATEGORIES = {
    "Programming Languages": {
        "python", "java", "c++", "c#", "c", "javascript", "typescript", "golang", "go",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "html", "html5",
        "css", "css3", "sql", "pl/sql", "bash", "shell", "powershell", "dart", "assembly", "perl"
    },
    "Web & Backend Frameworks": {
        "flask", "django", "fastapi", "react", "react.js", "reactjs", "angular", "vue", "vue.js",
        "next.js", "nextjs", "node.js", "nodejs", "express", "express.js", "spring", "spring boot",
        "asp.net", ".net", "bootstrap", "tailwind", "tailwindcss", "redux", "graphql", "rest api",
        "restful api", "microservices", "websockets", "vite", "webpack"
    },
    "Databases & Cloud Infrastructure": {
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "oracle", "sql server",
        "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
        "terraform", "ansible", "jenkins", "git", "github", "ci/cd", "linux", "unix", "firebase",
        "supabase", "snowflake", "bigquery", "nginx"
    },
    "AI, ML & Data Analytics": {
        "machine learning", "deep learning", "nlp", "natural language processing", "computer vision",
        "data science", "data analysis", "data analytics", "data visualization", "pandas", "numpy",
        "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras", "opencv", "spark", "pyspark",
        "tableau", "power bi", "llm", "generative ai", "neural networks"
    },
    "Engineering Practices & Tools": {
        "object-oriented programming", "oop", "data structures", "algorithms", "system design",
        "agile", "scrum", "kanban", "tdd", "unit testing", "debugging", "version control"
    }
}


def get_customized_resume_analysis(resume_text):
    """
    Produces a detailed, structured, customized data analysis breakdown of the candidate's resume
    with categorized skills, quantitative metrics, ATS health indicators, and clean output formatting.
    """
    if not resume_text:
        return {
            "overall_quality_score": 0.0,
            "total_skills_count": 0,
            "categorized_skills": {},
            "all_skills": [],
            "quantitative_metrics": {},
            "sections": {},
            "contact_info": {}
        }

    score, structure = analyze_resume_structure(resume_text)
    skills = extract_skills(resume_text)
    skills_lower = {s.lower(): s for s in skills}

    categorized_skills = {}
    categorized_set = set()

    for category, category_skills in SKILL_CATEGORIES.items():
        found = []
        for s_lower, canonical in skills_lower.items():
            if s_lower in category_skills:
                found.append(canonical)
                categorized_set.add(s_lower)
        categorized_skills[category] = sorted(found)

    # Any remaining skills placed in General Technical Competencies
    other_skills = [
        canonical for s_lower, canonical in skills_lower.items()
        if s_lower not in categorized_set
    ]
    if other_skills:
        categorized_skills["General Technical Competencies"] = sorted(other_skills)

    # Quantitative metrics
    words = resume_text.split()
    word_count = len(words)
    char_count = len(resume_text)
    sentences = [s for s in re.split(r'[.!?]+', resume_text) if s.strip()]
    sentence_count = max(1, len(sentences))
    avg_words_per_sentence = round(word_count / sentence_count, 1)
    reading_time_sec = max(10, round((word_count / 200) * 60))

    # Action verbs
    detected_action_verbs = sorted(list({
        w.capitalize() for w in words if w.lower() in ACTION_WORDS
    }))

    # Detected metrics (e.g. 40%, $10k, 5+ years, 100+ users)
    metrics_matches = re.findall(
        r'(\b\d+%(?!\w)|\$\d+[kKmMbB]?|\b\d+\+\b|\b\d+\s*(?:users|clients|projects|years|team\s*members|downloads|requests|customers)\b)',
        resume_text,
        flags=re.IGNORECASE
    )
    detected_metrics = sorted(list(set(metrics_matches[:10])))

    # Contact details
    emails = [m.group(0) for m in re.finditer(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)]
    phones = [m.group(0) for m in re.finditer(r'(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}', resume_text)]
    links = [m.group(0) for m in re.finditer(r'(?:https?://[^\s]+|linkedin\.com/[^\s]+|github\.com/[^\s]+)', resume_text, flags=re.IGNORECASE)]

    return {
        "overall_quality_score": score,
        "total_skills_count": len(skills),
        "categorized_skills": categorized_skills,
        "all_skills": skills,
        "quantitative_metrics": {
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "avg_words_per_sentence": avg_words_per_sentence,
            "reading_time_sec": reading_time_sec,
            "action_verb_count": len(detected_action_verbs),
            "detected_action_verbs": detected_action_verbs,
            "has_metrics": len(detected_metrics) > 0,
            "detected_metrics": detected_metrics,
            "length_rating": "Optimal (250-800 words)" if 250 <= word_count <= 850 else ("Needs More Content" if word_count < 250 else "Too Long")
        },
        "sections": structure.get("sections", {}),
        "contact_info": {
            "email": emails[0] if emails else "Not detected",
            "phone": phones[0] if phones else "Not detected",
            "links": links[:4],
            "is_complete": bool(emails and phones)
        }
    }
