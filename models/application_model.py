import sqlite3
from db import get_db


class JobApplicationModel:
    """Data access layer for candidate job applications and auto-apply audit logs."""

    @staticmethod
    def apply_internal(
        job_listing_id,
        user_id,
        resume_id,
        cover_letter=None,
        match_score=0.0,
        is_auto_applied=0,
        notes=None,
    ):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                """INSERT INTO job_applications
                   (job_listing_id, user_id, resume_id, cover_letter, status, match_score, is_auto_applied, notes)
                   VALUES (?, ?, ?, ?, 'pending', ?, ?, ?)""",
                (
                    job_listing_id,
                    user_id,
                    resume_id,
                    cover_letter.strip() if cover_letter else None,
                    float(match_score or 0.0),
                    int(bool(is_auto_applied)),
                    notes.strip() if notes else None,
                ),
            )
            db.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            db.rollback()
            raise

    @staticmethod
    def has_user_applied(job_listing_id, user_id):
        db = get_db()
        row = db.execute(
            "SELECT * FROM job_applications WHERE job_listing_id = ? AND user_id = ?",
            (job_listing_id, user_id),
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_user_applications(user_id, status_filter=None):
        db = get_db()
        query = """
            SELECT ja.*, jl.title as job_title, jl.company, jl.location,
                   jl.application_type, jl.is_active as listing_is_active,
                   r.filename as resume_filename
            FROM job_applications ja
            JOIN job_listings jl ON ja.job_listing_id = jl.id
            LEFT JOIN resumes r ON ja.resume_id = r.id
            WHERE ja.user_id = ?
        """
        params = [user_id]
        if status_filter and status_filter != 'all':
            query += " AND LOWER(ja.status) = LOWER(?)"
            params.append(status_filter.strip())
        query += " ORDER BY ja.applied_at DESC"
        rows = db.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_application_stats(user_id):
        """Return aggregate application counts for a candidate."""
        apps = JobApplicationModel.get_user_applications(user_id)
        stats = {
            'total': len(apps),
            'pending': 0,
            'reviewed': 0,
            'shortlisted': 0,
            'accepted': 0,
            'rejected': 0,
            'auto_applied': 0,
            'manual': 0,
        }
        for item in apps:
            status = (item.get('status') or 'pending').lower()
            if status in stats:
                stats[status] += 1
            if item.get('is_auto_applied'):
                stats['auto_applied'] += 1
            else:
                stats['manual'] += 1
        return stats

    @staticmethod
    def withdraw_application(application_id, user_id):
        """Allow a user to withdraw their own pending application."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM job_applications WHERE id = ? AND user_id = ? AND LOWER(status) = 'pending'",
            (application_id, user_id),
        )
        db.commit()
        return cursor.rowcount > 0

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
            (status.strip(), application_id),
        )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def log_auto_apply_run(
        user_id,
        resume_id,
        min_match_score,
        location_filter,
        max_applications,
        jobs_evaluated,
        applications_submitted,
        skipped_count,
    ):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO auto_apply_logs
               (user_id, resume_id, min_match_score, location_filter, max_applications,
                jobs_evaluated, applications_submitted, skipped_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                resume_id,
                float(min_match_score),
                location_filter.strip() if location_filter else None,
                int(max_applications),
                int(jobs_evaluated),
                int(applications_submitted),
                int(skipped_count),
            ),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_auto_apply_history(user_id, limit=10):
        db = get_db()
        rows = db.execute(
            """
            SELECT l.*, r.filename as resume_filename
            FROM auto_apply_logs l
            LEFT JOIN resumes r ON l.resume_id = r.id
            WHERE l.user_id = ?
            ORDER BY l.created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
