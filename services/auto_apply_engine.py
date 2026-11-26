import sqlite3
from models.user_model import UserModel
from models.resume_model import ResumeModel
from models.job_model import JobListingModel
from models.application_model import JobApplicationModel
from services.recommendation_engine import recommend_jobs_for_resume


def generate_tailored_cover_letter(candidate_name, job_title, company, matching_skills, match_score):
    """Build a concise, personalized cover letter tailored to the matched job."""
    name = (candidate_name or "Candidate").strip()
    skills_list = matching_skills[:6] if matching_skills else []
    if skills_list:
        skills_phrase = ", ".join(skills_list)
        body_skills = (
            f"My technical background aligns strongly with your requirements ({match_score}% skill match), "
            f"with hands-on experience in {skills_phrase}."
        )
    else:
        body_skills = (
            "I bring a strong software engineering foundation and adaptability to contribute immediately to your team."
        )

    return (
        f"Dear Hiring Team at {company},\n\n"
        f"I am excited to apply for the {job_title} position at {company}. "
        f"{body_skills} "
        f"I would welcome the opportunity to discuss how my experience can support {company}'s engineering goals.\n\n"
        f"Best regards,\n{name}"
    )


def preview_auto_apply(
    user_id,
    resume_id,
    min_match_score=60.0,
    location=None,
    max_applications=5,
):
    """
    Evaluate all active jobs for a user's resume without submitting applications.
    Categorizes jobs into eligible, already_applied, below_threshold, and external_jobs.
    """
    resume = ResumeModel.get_by_id(resume_id, user_id)
    if not resume:
        raise ValueError("Selected resume not found or does not belong to the user.")

    user = UserModel.get_by_id(user_id)
    candidate_name = user['name'] if user else "Candidate"

    min_score = max(0.0, min(100.0, float(min_match_score)))
    max_apps = max(1, min(50, int(max_applications)))

    active_listings = JobListingModel.get_active_listings()
    ranked_jobs = recommend_jobs_for_resume(
        resume_text=resume['resume_text'],
        active_listings=active_listings,
        location=location,
        limit=None,
    )

    existing_apps = JobApplicationModel.get_user_applications(user_id)
    applied_ids = {app['job_listing_id'] for app in existing_apps}

    eligible_all = []
    already_applied = []
    below_threshold = []
    external_jobs = []

    for job in ranked_jobs:
        if job['id'] in applied_ids:
            already_applied.append(job)
            continue

        if job.get('application_type') == 'external':
            external_jobs.append(job)
            continue

        if job['match_score'] < min_score:
            below_threshold.append(job)
            continue

        job_copy = dict(job)
        job_copy['cover_letter_preview'] = generate_tailored_cover_letter(
            candidate_name=candidate_name,
            job_title=job['title'],
            company=job['company'],
            matching_skills=job.get('matching_skills', []),
            match_score=job['match_score'],
        )
        eligible_all.append(job_copy)

    selected_batch = eligible_all[:max_apps]

    return {
        "resume": dict(resume),
        "min_match_score": min_score,
        "location_filter": location or "",
        "max_applications": max_apps,
        "total_evaluated": len(ranked_jobs),
        "eligible_jobs": selected_batch,
        "total_eligible_count": len(eligible_all),
        "already_applied": already_applied,
        "below_threshold": below_threshold,
        "external_jobs": external_jobs,
    }


def execute_auto_apply(
    user_id,
    resume_id,
    min_match_score=60.0,
    location=None,
    max_applications=5,
    selected_job_ids=None,
    custom_cover_letter=None,
):
    """
    Execute auto-apply for eligible internal job listings matching the user's resume
    and threshold criteria, logging the batch run in auto_apply_logs.
    """
    preview = preview_auto_apply(
        user_id=user_id,
        resume_id=resume_id,
        min_match_score=min_match_score,
        location=location,
        max_applications=max_applications,
    )

    candidates = preview['eligible_jobs']
    if selected_job_ids is not None:
        selected_set = {int(jid) for jid in selected_job_ids}
        candidates = [job for job in candidates if job['id'] in selected_set]

    applied_jobs = []
    skipped_jobs = []

    for job in candidates:
        cover_letter = (
            custom_cover_letter.strip()
            if custom_cover_letter and custom_cover_letter.strip()
            else job['cover_letter_preview']
        )
        try:
            app_id = JobApplicationModel.apply_internal(
                job_listing_id=job['id'],
                user_id=user_id,
                resume_id=resume_id,
                cover_letter=cover_letter,
                match_score=job['match_score'],
                is_auto_applied=1,
                notes=f"Auto-applied via AI engine ({job['match_score']}% skill match)",
            )
            applied_entry = dict(job)
            applied_entry['application_id'] = app_id
            applied_jobs.append(applied_entry)
        except sqlite3.IntegrityError:
            skipped_jobs.append({
                "id": job['id'],
                "title": job['title'],
                "company": job['company'],
                "reason": "Already applied",
            })

    skipped_count = len(skipped_jobs) + len(preview['already_applied']) + len(preview['external_jobs'])
    run_id = JobApplicationModel.log_auto_apply_run(
        user_id=user_id,
        resume_id=resume_id,
        min_match_score=preview['min_match_score'],
        location_filter=location,
        max_applications=preview['max_applications'],
        jobs_evaluated=preview['total_evaluated'],
        applications_submitted=len(applied_jobs),
        skipped_count=skipped_count,
    )

    return {
        "run_id": run_id,
        "applied_count": len(applied_jobs),
        "skipped_count": len(skipped_jobs),
        "applied_jobs": applied_jobs,
        "skipped_jobs": skipped_jobs,
        "total_evaluated": preview['total_evaluated'],
    }
