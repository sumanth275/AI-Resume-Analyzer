import sqlite3
from database.db import get_db
from services.skill_extractor import extract_skills

class JobListingModel:
    @staticmethod
    def get_active_listings(search=None, location=None):
        db = get_db()
        query = """
            SELECT jl.*, u.name as creator_name,
                   (SELECT COUNT(*) FROM job_applications ja WHERE ja.job_listing_id = jl.id) as applicant_count
            FROM job_listings jl
            LEFT JOIN users u ON jl.created_by = u.id
            WHERE jl.is_active = 1
        """
        params = []
        if search:
            query += " AND (jl.title LIKE ? OR jl.company LIKE ? OR jl.required_skills LIKE ? OR jl.description LIKE ?)"
            term = f"%{search.strip()}%"
            params.extend([term, term, term, term])
            
        if location:
            query += " AND jl.location LIKE ?"
            params.append(f"%{location.strip()}%")
            
        query += " ORDER BY jl.created_at DESC"
        return db.execute(query, params).fetchall()

    @staticmethod
    def get_all_listings():
        db = get_db()
        query = """
            SELECT jl.*, u.name as creator_name,
                   (SELECT COUNT(*) FROM job_applications ja WHERE ja.job_listing_id = jl.id) as applicant_count
            FROM job_listings jl
            LEFT JOIN users u ON jl.created_by = u.id
            ORDER BY jl.created_at DESC
        """
        return db.execute(query).fetchall()

    @staticmethod
    def get_by_id(listing_id):
        db = get_db()
        query = """
            SELECT jl.*, u.name as creator_name,
                   (SELECT COUNT(*) FROM job_applications ja WHERE ja.job_listing_id = jl.id) as applicant_count
            FROM job_listings jl
            LEFT JOIN users u ON jl.created_by = u.id
            WHERE jl.id = ?
        """
        return db.execute(query, (listing_id,)).fetchone()

    @staticmethod
    def create_listing(title, company, location, description, required_skills,
                       application_type, application_url, is_active=1, created_by=None):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO job_listings 
               (title, company, location, description, required_skills, application_type, application_url, is_active, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (title.strip(), company.strip(), location.strip() if location else None,
             description.strip(), required_skills.strip() if required_skills else None,
             application_type.strip(), application_url.strip() if application_url else None,
             int(is_active), created_by)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update_listing(listing_id, title, company, location, description, required_skills,
                       application_type, application_url, is_active=1):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE job_listings
               SET title = ?, company = ?, location = ?, description = ?, required_skills = ?,
                   application_type = ?, application_url = ?, is_active = ?
               WHERE id = ?""",
            (title.strip(), company.strip(), location.strip() if location else None,
             description.strip(), required_skills.strip() if required_skills else None,
             application_type.strip(), application_url.strip() if application_url else None,
             int(is_active), listing_id)
        )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def toggle_status(listing_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE job_listings SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?",
            (listing_id,)
        )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def delete_listing(listing_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM job_listings WHERE id = ?", (listing_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def get_recommended_listings(resume_text=None, resume_skills=None, limit=6):
        """
        Ranks active job listings based on skills extracted from user's resume.
        """
        active_jobs = JobListingModel.get_active_listings()
        if not active_jobs:
            return []

        if not resume_skills:
            if resume_text:
                resume_skills = extract_skills(resume_text)
            else:
                resume_skills = []

        resume_skills_lower = {s.lower() for s in resume_skills}

        recommendations = []
        for job in active_jobs:
            job_dict = dict(job)
            
            # Combine skills listed in required_skills and description
            job_skills = set()
            if job_dict.get('required_skills'):
                # Split comma separated or extract
                skills_list = [s.strip() for s in job_dict['required_skills'].split(',') if s.strip()]
                for s in skills_list:
                    job_skills.add(s)
            
            # Also extract skills from job description
            if job_dict.get('description'):
                for s in extract_skills(job_dict['description']):
                    job_skills.add(s)

            job_skills_lower = {s.lower() for s in job_skills}
            
            matching = [s for s in job_skills if s.lower() in resume_skills_lower]
            missing = [s for s in job_skills if s.lower() not in resume_skills_lower]

            if job_skills:
                match_percentage = round((len(matching) / len(job_skills)) * 100, 1)
            else:
                match_percentage = 50.0  # Default neutral score if no specific skills listed

            job_dict['match_score'] = match_percentage
            job_dict['matching_skills'] = matching
            job_dict['missing_skills'] = missing
            job_dict['total_skills_count'] = len(job_skills)
            recommendations.append(job_dict)

        # Sort descending by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:limit]


class JobApplicationModel:
    @staticmethod
    def apply_internal(job_listing_id, user_id, resume_id, cover_letter=None):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                """INSERT INTO job_applications 
                   (job_listing_id, user_id, resume_id, cover_letter, status)
                   VALUES (?, ?, ?, ?, 'pending')""",
                (job_listing_id, user_id, resume_id, cover_letter.strip() if cover_letter else None)
            )
            db.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            db.rollback()
            raise e

    @staticmethod
    def has_user_applied(job_listing_id, user_id):
        db = get_db()
        row = db.execute(
            "SELECT * FROM job_applications WHERE job_listing_id = ? AND user_id = ?",
            (job_listing_id, user_id)
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_user_applications(user_id):
        db = get_db()
        query = """
            SELECT ja.*, jl.title as job_title, jl.company, jl.location,
                   jl.application_type, jl.is_active as listing_is_active,
                   r.filename as resume_filename
            FROM job_applications ja
            JOIN job_listings jl ON ja.job_listing_id = jl.id
            LEFT JOIN resumes r ON ja.resume_id = r.id
            WHERE ja.user_id = ?
            ORDER BY ja.applied_at DESC
        """
        rows = db.execute(query, (user_id,)).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_applications_by_listing(job_listing_id):
        db = get_db()
        query = """
            SELECT ja.*, u.name as applicant_name, u.email as applicant_email,
                   r.filename as resume_filename, r.filepath as resume_filepath
            FROM job_applications ja
            JOIN users u ON ja.user_id = u.id
            LEFT JOIN resumes r ON ja.resume_id = r.id
            WHERE ja.job_listing_id = ?
            ORDER BY ja.applied_at DESC
        """
        rows = db.execute(query, (job_listing_id,)).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def update_status(application_id, status):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE job_applications 
               SET status = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE id = ?""",
            (status.strip(), application_id)
        )
        db.commit()
        return cursor.rowcount > 0
