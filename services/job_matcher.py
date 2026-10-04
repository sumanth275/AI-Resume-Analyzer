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