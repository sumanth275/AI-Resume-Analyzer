from collections import Counter
from services.skill_extractor import extract_skills
from services.job_matcher import (
    calculate_multiple_job_matches,
    get_career_recommendation,
    get_strongest_skill_and_recommendation,
)


def _matches_location_filter(job_location, location_filter):
    """Return True if job_location matches the requested location filter."""
    if not location_filter:
        return True
    loc_norm = (job_location or '').lower()
    req_norm = location_filter.strip().lower()
    if req_norm in ('bangalore', 'bengaluru'):
        return 'bangalore' in loc_norm or 'bengaluru' in loc_norm
    return req_norm in loc_norm


def _build_recommendation_reason(match_score, matching_skills, matches_strongest_skill, strongest_skill):
    """Generate a concise human-readable explanation for why a job is recommended."""
    if matches_strongest_skill and strongest_skill and matching_skills:
        return (
            f"Matches your strongest skill ({strongest_skill.title()}) and "
            f"{len(matching_skills)} required skills ({match_score}% fit)."
        )
    if matching_skills:
        top_skills = ", ".join(matching_skills[:3])
        return f"Aligns with {len(matching_skills)} of your skills including {top_skills}."
    return "Recommended as an adjacent growth opportunity to expand your tech stack."


def recommend_jobs_for_resume(
    resume_text=None,
    resume_skills=None,
    active_listings=None,
    location=None,
    min_score=0.0,
    limit=25,
):
    """
    Score and rank active job listings against extracted resume skills.
    """
    if active_listings is None:
        from models.job_model import JobListingModel
        active_listings = JobListingModel.get_active_listings()

    if not active_listings:
        return []

    if not resume_skills:
        resume_skills = extract_skills(resume_text) if resume_text else []

    resume_skills_lower = {s.lower() for s in resume_skills}
    strongest_skill = resume_skills[0].lower() if resume_skills else None

    recommendations = []
    for job in active_listings:
        job_dict = dict(job)
        if not _matches_location_filter(job_dict.get('location'), location):
            continue

        job_skills = set()
        if job_dict.get('required_skills'):
            for skill in job_dict['required_skills'].split(','):
                cleaned = skill.strip()
                if cleaned:
                    job_skills.add(cleaned)

        if job_dict.get('description'):
            for skill in extract_skills(job_dict['description']):
                job_skills.add(skill)

        job_skills_lower = {s.lower() for s in job_skills}
        matching = sorted(s for s in job_skills if s.lower() in resume_skills_lower)
        missing = sorted(s for s in job_skills if s.lower() not in resume_skills_lower)

        if job_skills:
            match_percentage = round((len(matching) / len(job_skills)) * 100, 1)
        else:
            match_percentage = 50.0

        if min_score and match_percentage < float(min_score):
            continue

        matches_strongest = (strongest_skill in job_skills_lower) if strongest_skill else False

        job_dict['match_score'] = match_percentage
        job_dict['matching_skills'] = matching
        job_dict['missing_skills'] = missing
        job_dict['total_skills_count'] = len(job_skills)
        job_dict['matches_strongest_skill'] = matches_strongest
        job_dict['recommendation_reason'] = _build_recommendation_reason(
            match_percentage, matching, matches_strongest, strongest_skill
        )
        recommendations.append(job_dict)

    recommendations.sort(
        key=lambda x: (x['match_score'], 1 if x['matches_strongest_skill'] else 0),
        reverse=True,
    )
    return recommendations[:limit] if limit else recommendations


def get_skill_gap_roadmap(recommended_jobs, top_n=8):
    """
    Aggregate the most commonly missing skills across recommended jobs
    to surface the highest-ROI skills to learn next.
    """
    counter = Counter()
    for job in recommended_jobs or []:
        for skill in job.get('missing_skills', []):
            counter[skill] += 1

    roadmap = []
    for skill, demand in counter.most_common(top_n):
        priority = "High" if demand >= 4 else ("Medium" if demand >= 2 else "Nice to Have")
        roadmap.append({
            "skill": skill,
            "demand_count": demand,
            "priority": priority,
        })
    return roadmap


def get_personalized_career_bundle(resume_text, active_listings=None, location=None, limit=25):
    """
    Return a unified recommendation bundle combining strongest skill insight,
    role matches, career direction, ranked job listings, and skill-gap roadmap.
    """
    if not resume_text:
        return {
            "strongest_rec": None,
            "role_matches": [],
            "career_rec": None,
            "recommended_jobs": [],
            "skill_gap_roadmap": [],
        }

    role_matches = calculate_multiple_job_matches(resume_text)
    strongest_rec = get_strongest_skill_and_recommendation(resume_text, role_matches)
    career_rec = get_career_recommendation(resume_text, role_matches)
    recommended_jobs = recommend_jobs_for_resume(
        resume_text=resume_text,
        active_listings=active_listings,
        location=location,
        limit=limit,
    )
    skill_gap_roadmap = get_skill_gap_roadmap(recommended_jobs[:10])

    return {
        "strongest_rec": strongest_rec,
        "role_matches": role_matches,
        "career_rec": career_rec,
        "recommended_jobs": recommended_jobs,
        "skill_gap_roadmap": skill_gap_roadmap,
    }
