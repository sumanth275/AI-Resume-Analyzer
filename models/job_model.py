from db import get_db


class JobModel:
    """Data access layer for custom target job descriptions submitted for analysis."""

    @staticmethod
    def save_job(user_id, title, description):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO jobs (user_id, title, description) VALUES (?, ?, ?)",
            (user_id, title, description)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_id(job_id):
        db = get_db()
        return db.execute(
            "SELECT * FROM jobs WHERE id = ?",
            (job_id,)
        ).fetchone()


class JobListingModel:
    """Data access layer for portal job listings."""

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
    def create_listing(
        title,
        company,
        location,
        description,
        required_skills,
        application_type,
        application_url,
        is_active=1,
        created_by=None,
    ):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO job_listings
               (title, company, location, description, required_skills, application_type, application_url, is_active, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                title.strip(),
                company.strip(),
                location.strip() if location else None,
                description.strip(),
                required_skills.strip() if required_skills else None,
                application_type.strip(),
                application_url.strip() if application_url else None,
                int(is_active),
                created_by,
            ),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update_listing(
        listing_id,
        title,
        company,
        location,
        description,
        required_skills,
        application_type,
        application_url,
        is_active=1,
    ):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """UPDATE job_listings
               SET title = ?, company = ?, location = ?, description = ?, required_skills = ?,
                   application_type = ?, application_url = ?, is_active = ?
               WHERE id = ?""",
            (
                title.strip(),
                company.strip(),
                location.strip() if location else None,
                description.strip(),
                required_skills.strip() if required_skills else None,
                application_type.strip(),
                application_url.strip() if application_url else None,
                int(is_active),
                listing_id,
            ),
        )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def toggle_status(listing_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE job_listings SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?",
            (listing_id,),
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
    def get_recommended_listings(resume_text=None, resume_skills=None, limit=25):
        """Rank active job listings based on skills extracted from the user's resume."""
        from services.recommendation_engine import recommend_jobs_for_resume

        active_jobs = JobListingModel.get_active_listings()
        return recommend_jobs_for_resume(
            resume_text=resume_text,
            resume_skills=resume_skills,
            active_listings=active_jobs,
            limit=limit,
        )
