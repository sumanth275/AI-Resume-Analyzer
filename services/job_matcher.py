from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from services.text_processor import preprocess_text
from services.skill_extractor import extract_skills
from services.resume_analyzer import analyze_resume_structure
from services.job_roles import get_job_roles


def calculate_job_match(resume_text, job_description):
    """
    NLP / ML Engine:
    1. Preprocesses resume & job description text.
    2. Vectorizes text using TF-IDF.
    3. Calculates Cosine Similarity for keyword match.
    4. Extracts skills & calculates skill overlap.
    5. Evaluates standalone Resume Score.
    6. Synthesizes overall Job Match Score & tailored Recommendations.
    """
    if not resume_text or not job_description:
        return {
            'match_score': 0.0,
            'resume_score': 0.0,
            'skills_match_score': 0.0,
            'keyword_match_score': 0.0,
            'matching_skills': [],
            'missing_skills': [],
            'recommendations': [
                "Please provide both a valid resume and job description."
            ]
        }

    # Preprocess text for TF-IDF
    processed_resume = preprocess_text(resume_text)
    processed_job = preprocess_text(job_description)

    # 1. TF-IDF & Cosine Similarity
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))

    try:
        tfidf_matrix = vectorizer.fit_transform(
            [processed_resume, processed_job]
        )

        similarity = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]

        keyword_match_score = round(float(similarity) * 100, 1)

    except Exception:
        keyword_match_score = 0.0

    # 2. Skill Extraction & Overlap
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description))

    if job_skills:
        matching_skills = sorted(
            list(resume_skills.intersection(job_skills))
        )

        missing_skills = sorted(
            list(job_skills.difference(resume_skills))
        )

        skills_match_score = round(
            (len(matching_skills) / len(job_skills)) * 100,
            1
        )

    else:
        matching_skills = sorted(list(resume_skills))
        missing_skills = []
        skills_match_score = keyword_match_score

    # 3. Resume Structural Score
    resume_score, structure_details = analyze_resume_structure(
        resume_text
    )

    # 4. Overall Weighted Job Match Score
    # 50% Skill Match
    # 35% Keyword TF-IDF Match
    # 15% Resume Structural Score

    overall_score = (
        (0.50 * skills_match_score)
        + (0.35 * keyword_match_score)
        + (0.15 * resume_score)
    )

    overall_score = round(
        min(100.0, max(0.0, overall_score)),
        1
    )

    # 5. Recommendation Engine
    recommendations = generate_recommendations(
        overall_score,
        resume_score,
        skills_match_score,
        keyword_match_score,
        matching_skills,
        missing_skills,
        structure_details
    )

    return {
        'match_score': overall_score,
        'resume_score': resume_score,
        'skills_match_score': skills_match_score,
        'keyword_match_score': keyword_match_score,
        'matching_skills': matching_skills,
        'missing_skills': missing_skills,
        'recommendations': recommendations
    }


def generate_recommendations(
    match_score,
    resume_score,
    skills_score,
    keyword_score,
    matching_skills,
    missing_skills,
    structure_details
):
    """
    Generates actionable, personalized suggestions
    to improve resume alignment with the job.
    """

    recs = []

    # Missing Skills Recommendations
    if missing_skills:
        top_missing = missing_skills[:5]
        skills_str = ", ".join(top_missing)

        recs.append(
            f"Add key missing skills to your resume: {skills_str}."
        )

        if len(missing_skills) > 5:
            recs.append(
                "Highlight additional required technical tools such as "
                + ", ".join(missing_skills[5:8])
                + "."
            )

    # Keyword / TF-IDF Density Recommendations
    if keyword_score < 60:
        recs.append(
            "Tailor your professional summary and experience "
            "bullet points using exact phrases from the job description."
        )

    elif keyword_score < 80:
        recs.append(
            "Incorporate more industry-specific terminology "
            "to increase your ATS keyword match score."
        )

    # Section Gaps Recommendations
    missing_sections = structure_details.get(
        'sections',
        {}
    ).get(
        'missing',
        []
    )

    if missing_sections:
        sec_str = ", ".join(missing_sections)

        recs.append(
            f"Consider adding missing standard sections: {sec_str}."
        )

    # Measurable Results & Impact Recommendations
    impact_info = structure_details.get(
        'impact',
        {}
    )

    if not impact_info.get('has_metrics'):
        recs.append(
            "Add quantitative achievements "
            "(e.g., 'Increased performance by 30%', "
            "'Managed $50K budget')."
        )

    if impact_info.get('action_verb_count', 0) < 5:
        recs.append(
            "Use stronger action verbs at the beginning of "
            "bullet points (e.g., Developed, Orchestrated, "
            "Optimized, Spearheaded)."
        )

    # Formatting & Contact Recommendations
    contact_info = structure_details.get(
        'contact_info',
        {}
    )

    if not contact_info.get('has_link'):
        recs.append(
            "Include your LinkedIn profile link or GitHub "
            "portfolio URL in the contact header."
        )

    # Overall encouragement
    if match_score < 50:
        recs.append(
            "Your resume currently has a low match with this "
            "job posting. Consider tailoring your experience "
            "descriptions specifically for this role."
        )

    elif match_score >= 80:
        recs.append(
            "Great match! Your resume strongly aligns "
            "with the target job requirements."
        )

    return recs


def calculate_multiple_job_matches(resume_text):
    """
    Calculates the resume match score against all
    predefined job roles.
    """

    if not resume_text:
        return []

    job_roles = get_job_roles()
    results = []

    for role_name, role_data in job_roles.items():

        job_description = role_data["description"]

        analysis = calculate_job_match(
            resume_text,
            job_description
        )

        results.append({
            "job_role": role_name,
            "match_score": analysis["match_score"],
            "resume_score": analysis["resume_score"],
            "skills_match_score": analysis["skills_match_score"],
            "keyword_match_score": analysis["keyword_match_score"],
            "matching_skills": analysis["matching_skills"],
            "missing_skills": analysis["missing_skills"],
            "recommendations": analysis["recommendations"]
        })

    # Highest match first
    results.sort(
        key=lambda item: item["match_score"],
        reverse=True
    )

    return results


# ============================================================
# CAREER RECOMMENDATION & SKILL GAP ANALYSIS
# ============================================================

ROLE_PROJECT_TYPES = {
    "Python Developer": "build a Python backend/API project",
    "Data Analyst": "build a data analysis and dashboard project",
    "Machine Learning Engineer": "build an end-to-end machine learning project",
    "Data Scientist": "build a data science project",
    "Web Developer": "build a full-stack web application",
    "AI Engineer": "build an AI-powered application",
    "Deep Learning Engineer": "build a deep learning computer vision project",
    "NLP Engineer": "build an NLP text-processing project",
    "Computer Vision Engineer": "build a computer vision project",
    "Generative AI Engineer": "build a Generative AI application",
    "AI/ML Researcher": "build an AI/ML research-oriented project",
    "MLOps Engineer": "build an ML deployment and MLOps project",
    "Data Engineer": "build a data pipeline project",
    "Business Intelligence Analyst": "build a BI dashboard and reporting project",
    "Big Data Engineer": "build a big-data processing project",
    "Software Engineer": "build a complete software engineering project",
    "Backend Developer": "build a REST API backend project",
    "Full Stack Developer": "build a complete full-stack application",
    "AI Product Engineer": "build an AI-powered product prototype",
    "Robotics and AI Engineer": "build a robotics and AI project"
}


def generate_career_recommendation(multiple_role_results):
    """
    Generate career recommendation information from the existing
    job matching results without changing the existing scoring logic.
    """

    if not multiple_role_results:
        return {
            "top_jobs": [],
            "all_jobs": [],
            "best_job": None,
            "skill_gap": {
                "matching": [],
                "missing": [],
                "to_learn": []
            },
            "roadmap": [],
            "next_best_action": None
        }

    top_jobs = multiple_role_results[:5]
    best_job = top_jobs[0]

    matching_skills = best_job.get("matching_skills", [])
    missing_skills = best_job.get("missing_skills", [])

    skills_to_learn = missing_skills[:6]

    foundation = matching_skills[:3] if matching_skills else ["Foundational Programming", "Core CS Principles"]
    technical = missing_skills[:2] if len(missing_skills) >= 2 else (missing_skills + ["Core Frameworks"])
    tools = missing_skills[2:4] if len(missing_skills) >= 4 else (missing_skills[2:] if len(missing_skills) > 2 else ["Database Systems", "Git Version Control"])

    role = best_job.get("job_role", "your target role")
    match_score = best_job.get("match_score", 0)

    stage4_project_skill = ", ".join(missing_skills[:2]) if missing_skills else role

    roadmap = [
        {
            "stage": 1,
            "title": "Stage 1 — Foundation",
            "description": "Strengthen Your Foundation",
            "skills": foundation
        },
        {
            "stage": 2,
            "title": "Stage 2 — Technical Specialization",
            "description": "Learn Role-Specific Skills",
            "skills": technical
        },
        {
            "stage": 3,
            "title": "Stage 3 — Database & Tools",
            "description": "Practice Tools and Technologies",
            "skills": tools
        },
        {
            "stage": 4,
            "title": "Stage 4 — Job Preparation",
            "description": "Build Projects and Prepare for Interviews",
            "skills": [
                f"Build a practical project using {stage4_project_skill}",
                "Add project metrics and source code repository to resume",
                f"Practice {role} technical interview questions"
            ]
        }
    ]

    project_type = ROLE_PROJECT_TYPES.get(
        role,
        "build a practical project related to this role"
    )

    action_recommendation = (
        f"Start by {project_type}. "
        "Add it to your GitHub portfolio and use it to demonstrate "
        "your skills during interviews."
    )

    next_best_action = {
        "job_title": role,
        "match_score": match_score,
        "priority_skills": ", ".join(missing_skills[:3]) if missing_skills else "Portfolio & Applications",
        "action_text": f"Your strongest career path is {role} with a {match_score}% match.",
        "recommendation": action_recommendation
    }

    return {
        "top_jobs": top_jobs,
        "all_jobs": multiple_role_results,
        "best_job": best_job,
        "skill_gap": {
            "matching": matching_skills,
            "missing": missing_skills,
            "to_learn": skills_to_learn
        },
        "roadmap": roadmap,
        "next_best_action": next_best_action
    }


def get_career_recommendation(resume_text=None, multiple_role_results=None):
    """
    Return career recommendations using the existing job-match results.

    If results are not supplied, calculate them from the resume text.
    """

    if multiple_role_results is None:
        if not resume_text:
            return None

        multiple_role_results = calculate_multiple_job_matches(
            resume_text
        )

    if not multiple_role_results:
        return None

    return generate_career_recommendation(
        multiple_role_results
    )