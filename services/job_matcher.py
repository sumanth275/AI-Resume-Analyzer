from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from services.text_processor import preprocess_text
from services.skill_extractor import extract_skills
from services.resume_analyzer import analyze_resume_structure
from services.job_roles import get_job_roles, get_role_skills


def calculate_job_match(resume_text, job_description):
    """
    Calculates the match between a resume and a specific job description.
    """

    if not resume_text or not job_description:
        return {
            "match_score": 0.0,
            "resume_score": 0.0,
            "skills_match_score": 0.0,
            "keyword_match_score": 0.0,
            "matching_skills": [],
            "missing_skills": [],
            "recommendations": [
                "Please provide both a valid resume and job description."
            ]
        }

    # ---------------------------------------------------------
    # 1. TF-IDF KEYWORD MATCH
    # ---------------------------------------------------------

    processed_resume = preprocess_text(resume_text)
    processed_job = preprocess_text(job_description)

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2)
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(
            [processed_resume, processed_job]
        )

        similarity = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]

        keyword_match_score = round(
            float(similarity) * 100,
            1
        )

    except Exception:
        keyword_match_score = 0.0

    # ---------------------------------------------------------
    # 2. GENERAL SKILL MATCH
    # ---------------------------------------------------------

    resume_skills = set(
        extract_skills(resume_text)
    )

    job_skills = set(
        extract_skills(job_description)
    )

    if job_skills:

        matching_skills = sorted(
            resume_skills.intersection(job_skills)
        )

        missing_skills = sorted(
            job_skills.difference(resume_skills)
        )

        skills_match_score = round(
            (
                len(matching_skills)
                / len(job_skills)
            ) * 100,
            1
        )

    else:

        matching_skills = sorted(
            list(resume_skills)
        )

        missing_skills = []

        skills_match_score = keyword_match_score

    # ---------------------------------------------------------
    # 3. RESUME QUALITY
    # ---------------------------------------------------------

    resume_score, structure_details = (
        analyze_resume_structure(resume_text)
    )

    # ---------------------------------------------------------
    # 4. GENERAL JOB MATCH
    # ---------------------------------------------------------

    overall_score = (
        (0.50 * skills_match_score)
        + (0.35 * keyword_match_score)
        + (0.15 * resume_score)
    )

    overall_score = round(
        min(100.0, max(0.0, overall_score)),
        1
    )

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
        "match_score": overall_score,
        "resume_score": resume_score,
        "skills_match_score": skills_match_score,
        "keyword_match_score": keyword_match_score,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "recommendations": recommendations
    }


# =============================================================
# RESUME-BASED JOB ROLE RECOMMENDATION
# =============================================================

def calculate_multiple_job_matches(resume_text):
    """
    Compares the resume against all predefined job roles.

    The score considers:
    1. Technical Skills Match Percentage (matched required skills / total required skills * 100)
    2. Keyword similarity (secondary ranking factor)
    3. Overall Job Match score

    Returns roles ranked primarily by technical skills match percentage,
    with keyword similarity as a secondary ranking factor.
    """

    if not resume_text:
        return []

    job_roles = get_job_roles()

    resume_skills = set(
        extract_skills(resume_text)
    )

    results = []

    for role_name, role_data in job_roles.items():

        job_description = role_data["description"]

        analysis = calculate_job_match(
            resume_text,
            job_description
        )

        # -----------------------------------------------------
        # Role-specific required skills
        # -----------------------------------------------------

        role_skills = set(
            extract_skills(job_description)
        )

        matching_role_skills = sorted(
            resume_skills.intersection(role_skills)
        )

        missing_role_skills = sorted(
            role_skills.difference(resume_skills)
        )

        # -----------------------------------------------------
        # Technical Skills Match Percentage
        # (Matched required skills / total required skills * 100)
        # -----------------------------------------------------

        if role_skills:
            technical_skills_match_percentage = (
                len(matching_role_skills)
                / len(role_skills)
            ) * 100
        else:
            technical_skills_match_percentage = 0.0

        technical_skills_match_percentage = round(
            technical_skills_match_percentage,
            1
        )

        # -----------------------------------------------------
        # Role relevance score
        # -----------------------------------------------------

        role_relevance = calculate_role_relevance(
            resume_skills,
            role_skills
        )

        # -----------------------------------------------------
        # Overall job match score for this role
        # -----------------------------------------------------

        improved_score = (
            (0.45 * technical_skills_match_percentage)
            + (0.25 * analysis["keyword_match_score"])
            + (0.15 * analysis["resume_score"])
            + (0.15 * role_relevance)
        )

        improved_score = round(
            min(100.0, max(0.0, improved_score)),
            1
        )

        # -----------------------------------------------------
        # Career fit level
        # -----------------------------------------------------

        fit_level = get_fit_level(
            improved_score
        )

        # -----------------------------------------------------
        # Why this role is recommended
        # -----------------------------------------------------

        why_role = generate_role_reason(
            role_name,
            matching_role_skills,
            improved_score
        )

        # -----------------------------------------------------
        # Skills to improve
        # -----------------------------------------------------

        skills_to_improve = missing_role_skills[:8]

        # -----------------------------------------------------
        # Recommended skills to learn
        # -----------------------------------------------------

        recommended_skills = generate_skill_recommendations(
            resume_skills,
            missing_role_skills,
            role_name=role_name
        )

        # -----------------------------------------------------
        # Learning priority
        # -----------------------------------------------------

        learning_priority = create_learning_priority(
            resume_skills,
            missing_role_skills
        )

        results.append({
            "job_role": role_name,
            "technical_skills_match_percentage": technical_skills_match_percentage,
            "match_score": improved_score,
            "resume_score": analysis["resume_score"],
            "skills_match_score": analysis["skills_match_score"],
            "keyword_match_score": analysis["keyword_match_score"],
            "skill_coverage": technical_skills_match_percentage,
            "role_relevance": role_relevance,
            "fit_level": fit_level,
            "why_role": why_role,
            "matching_skills": matching_role_skills,
            "missing_skills": missing_role_skills,
            "skills_to_improve": skills_to_improve,
            "recommended_skills": recommended_skills,
            "learning_priority": learning_priority,
            "recommendations": analysis["recommendations"]
        })

    # ---------------------------------------------------------
    # Rank primarily by Technical Skills Match Percentage,
    # with Keyword Similarity as secondary ranking factor.
    # ---------------------------------------------------------

    results.sort(
        key=lambda item: (
            item["technical_skills_match_percentage"],
            item["keyword_match_score"],
            item["match_score"]
        ),
        reverse=True
    )

    # ---------------------------------------------------------
    # Difference from the next-best role
    # ---------------------------------------------------------

    for index, result in enumerate(results):
        if index == 0 and len(results) > 1:
            difference = (
                result["technical_skills_match_percentage"]
                - results[1]["technical_skills_match_percentage"]
            )
            result["difference_from_next"] = round(difference, 1)
        else:
            result["difference_from_next"] = 0.0

    return results


# =============================================================
# ROLE RELEVANCE
# =============================================================

def calculate_role_relevance(
    resume_skills,
    role_skills
):
    """
    Calculates how strongly the student's
    existing skills relate to the role.
    """

    if not role_skills:
        return 0.0

    matching = resume_skills.intersection(
        role_skills
    )

    if not matching:
        return 0.0

    coverage = (
        len(matching)
        / len(role_skills)
    ) * 100

    if len(matching) >= 5:

        coverage += 10

    elif len(matching) >= 3:

        coverage += 5

    return round(
        min(100.0, coverage),
        1
    )


# =============================================================
# FIT LEVEL
# =============================================================

def get_fit_level(score):

    if score >= 80:
        return "Excellent Fit"

    elif score >= 65:
        return "Strong Fit"

    elif score >= 50:
        return "Moderate Fit"

    elif score >= 35:
        return "Developing Fit"

    return "Needs Improvement"


# =============================================================
# ROLE EXPLANATION
# =============================================================

def generate_role_reason(
    role_name,
    matching_skills,
    score
):

    if matching_skills:

        top_skills = matching_skills[:5]

        skills_text = ", ".join(
            top_skills
        )

        if score >= 65:

            return (
                f"Your resume already contains "
                f"strong role-related skills such as "
                f"{skills_text}."
            )

        elif score >= 50:

            return (
                f"Your resume has useful skills for "
                f"{role_name}, including "
                f"{skills_text}. Strengthening "
                f"additional role-specific skills "
                f"can improve your fit."
            )

        else:

            return (
                f"You already have some relevant "
                f"skills such as {skills_text}. "
                f"Building more {role_name}-specific "
                f"skills will improve your career fit."
            )

    return (
        f"Your current resume has limited direct "
        f"skill coverage for {role_name}. "
        f"Learning the core skills for this role "
        f"is recommended."
    )


# =============================================================
# SKILL RECOMMENDATION ENGINE
# =============================================================

def generate_skill_recommendations(
    resume_skills,
    missing_core_skills,
    missing_supporting_skills=None,
    role_name="this role"
):
    recommendations = []

    if missing_supporting_skills is None:
        missing_supporting_skills = []

    # Ensure list types
    if isinstance(missing_core_skills, (set, tuple)):
        missing_core_skills = list(missing_core_skills)
    if isinstance(missing_supporting_skills, (set, tuple)):
        missing_supporting_skills = list(missing_supporting_skills)

    # Core skills first
    for skill in missing_core_skills[:5]:
        recommendations.append(
            f"Learn {skill} because it is a core skill for {role_name}."
        )

    # Supporting skills next
    for skill in missing_supporting_skills[:3]:
        recommendations.append(
            f"Improve {skill} to strengthen your {role_name} profile."
        )

    # Resume-based recommendations
    skill_names = {
        skill.lower()
        for skill in resume_skills
    }

    if "python" in skill_names:
        recommendations.append(
            "Build practical Python projects to demonstrate your programming skills."
        )

    if "sql" in skill_names:
        recommendations.append(
            "Practice SQL joins, queries and database-based projects."
        )

    if "machine learning" in skill_names:
        recommendations.append(
            "Build machine learning projects and practice model evaluation."
        )

    return recommendations[:10]


# =============================================================
# LEARNING PRIORITY
# =============================================================

def create_learning_priority(
    resume_skills,
    missing_core_skills,
    missing_supporting_skills=None
):
    priority = []

    if missing_supporting_skills is None:
        missing_supporting_skills = []

    # Ensure list types
    if isinstance(missing_core_skills, (set, tuple)):
        missing_core_skills = list(missing_core_skills)
    if isinstance(missing_supporting_skills, (set, tuple)):
        missing_supporting_skills = list(missing_supporting_skills)

    # Strengthen current skills first
    foundation_order = [
        "Python",
        "SQL",
        "Git",
        "HTML",
        "CSS",
        "JavaScript",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "Flask",
        "REST API",
        "Docker"
    ]

    normalized_resume = {
        skill.lower()
        for skill in resume_skills
    }

    for skill in foundation_order:
        if skill.lower() in normalized_resume:
            priority.append(
                f"Strengthen {skill}"
            )

    # Then learn missing core skills
    for skill in missing_core_skills:
        if len(priority) >= 8:
            break
        priority.append(
            f"Learn {skill}"
        )

    # Then supporting skills
    for skill in missing_supporting_skills:
        if len(priority) >= 8:
            break
        priority.append(
            f"Learn {skill}"
        )

    return priority


# =============================================================
# GENERAL RESUME RECOMMENDATIONS
# =============================================================

def generate_recommendations(
    match_score,
    resume_score,
    skills_score,
    keyword_score,
    matching_skills,
    missing_skills,
    structure_details
):

    recs = []

    # Skills
    if missing_skills:

        top_missing = missing_skills[:5]

        skills_str = ", ".join(
            top_missing
        )

        recs.append(
            f"Consider learning or improving "
            f"these relevant skills: {skills_str}."
        )

    # Keyword similarity
    if keyword_score < 60:

        recs.append(
            "Tailor your professional summary "
            "and project descriptions using "
            "relevant terms from the target job."
        )

    elif keyword_score < 80:

        recs.append(
            "Add more role-specific terminology "
            "naturally to your resume."
        )

    # Resume sections
    missing_sections = (
        structure_details
        .get("sections", {})
        .get("missing", [])
    )

    if missing_sections:

        sec_str = ", ".join(
            missing_sections
        )

        recs.append(
            f"Consider adding standard resume "
            f"sections: {sec_str}."
        )

    # Quantitative achievements
    impact_info = (
        structure_details
        .get("impact", {})
    )

    if not impact_info.get(
        "has_metrics"
    ):

        recs.append(
            "Add measurable project achievements "
            "where possible, such as accuracy, "
            "performance improvement or time saved."
        )

    # Action verbs
    if impact_info.get(
        "action_verb_count",
        0
    ) < 5:

        recs.append(
            "Use strong action verbs such as "
            "Developed, Designed, Implemented, "
            "Optimized and Automated."
        )

    # Contact links
    contact_info = (
        structure_details
        .get("contact_info", {})
    )

    if not contact_info.get(
        "has_link"
    ):

        recs.append(
            "Include your LinkedIn or GitHub "
            "portfolio link in the resume header."
        )

    # Score guidance
    if match_score < 35:

        recs.append(
            "Major skill improvement is recommended "
            "before applying for this role."
        )

    elif match_score < 50:

        recs.append(
            "Your resume is developing for this role. "
            "Focus on the recommended skills and projects."
        )

    elif match_score < 65:

        recs.append(
            "You have a moderate fit. Strengthening "
            "the missing skills can improve your match."
        )

    elif match_score < 80:

        recs.append(
            "You have a strong foundation for this role. "
            "Continue strengthening role-specific skills."
        )

    else:
        recs.append(
            "Excellent alignment with the target role. "
            "Continue building projects and measurable achievements."
        )

    return recs


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
    "Frontend Developer": "build an interactive modern web frontend project",
    "DevOps Engineer": "build a CI/CD and containerized deployment project",
    "Cloud Engineer": "build a cloud infrastructure and serverless project",
    "Cyber Security Analyst": "build a security audit and vulnerability assessment project",
    "Database Administrator": "build a relational database schema and query tuning project",
    "Mobile App Developer": "build a cross-platform mobile application",
    "QA Automation Engineer": "build an automated test suite with CI/CD integration",
    "Systems Software Engineer": "build a systems programming and memory management project",
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
            "next_best_action": None,
            "strongest_skill": None
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
    match_score = best_job.get("technical_skills_match_percentage", best_job.get("match_score", 0))

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


def get_strongest_skill_and_recommendation(resume_text=None, multiple_role_results=None):
    """
    Identifies candidate's strongest skill and recommends the best-fit job
    depending specifically on that strongest skill.
    """
    if not resume_text and not multiple_role_results:
        return {
            "strongest_skill": None,
            "recommended_role": None,
            "match_percentage": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "reason": "Please upload a resume to identify your strongest skill."
        }

    if multiple_role_results is None and resume_text:
        multiple_role_results = calculate_multiple_job_matches(resume_text)

    if not multiple_role_results:
        return {
            "strongest_skill": None,
            "recommended_role": None,
            "match_percentage": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "reason": "No matched roles found."
        }

    # Weight skills by how many roles they match and the rank of those roles
    skill_weights = {}
    for idx, role in enumerate(multiple_role_results):
        weight = max(1, 25 - idx)
        for s in role.get("matching_skills", []):
            skill_weights[s] = skill_weights.get(s, 0) + weight

    if not skill_weights:
        # Fallback to skills extracted directly
        extracted = extract_skills(resume_text) if resume_text else []
        if extracted:
            strongest_skill = extracted[0]
        else:
            return {
                "strongest_skill": None,
                "recommended_role": multiple_role_results[0]["job_role"],
                "match_percentage": multiple_role_results[0]["technical_skills_match_percentage"],
                "matched_skills": multiple_role_results[0].get("matching_skills", []),
                "missing_skills": multiple_role_results[0].get("missing_skills", []),
                "reason": f"Recommended role: {multiple_role_results[0]['job_role']}."
            }
    else:
        strongest_skill = max(skill_weights.items(), key=lambda x: x[1])[0]

    # Find the top role where strongest_skill is present
    matched_roles = [
        r for r in multiple_role_results
        if strongest_skill in r.get("matching_skills", [])
    ]
    target_role = matched_roles[0] if matched_roles else multiple_role_results[0]

    return {
        "strongest_skill": strongest_skill,
        "recommended_role": target_role["job_role"],
        "match_percentage": target_role.get("technical_skills_match_percentage", target_role.get("match_score", 0)),
        "matched_skills": target_role.get("matching_skills", []),
        "missing_skills": target_role.get("missing_skills", []),
        "reason": f"Your strongest skill identified is {strongest_skill}. Based on this strength, {target_role['job_role']} is your recommended career path with a {target_role.get('technical_skills_match_percentage', 0)}% skill match."
    }