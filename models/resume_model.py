import json
from db import get_db


class ResumeModel:
    """Data access layer for uploaded user resumes."""

    @staticmethod
    def save_resume(user_id, filename, filepath, resume_text):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO resumes (user_id, filename, filepath, resume_text) VALUES (?, ?, ?, ?)",
            (user_id, filename, filepath, resume_text)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_user(user_id):
        db = get_db()
        return db.execute(
            "SELECT * FROM resumes WHERE user_id = ? ORDER BY uploaded_at DESC",
            (user_id,)
        ).fetchall()

    @staticmethod
    def get_by_id(resume_id, user_id=None):
        db = get_db()
        if user_id:
            return db.execute(
                "SELECT * FROM resumes WHERE id = ? AND user_id = ?",
                (resume_id, user_id)
            ).fetchone()
        return db.execute(
            "SELECT * FROM resumes WHERE id = ?",
            (resume_id,)
        ).fetchone()

    @staticmethod
    def delete_resume(resume_id, user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM resumes WHERE id = ? AND user_id = ?",
            (resume_id, user_id)
        )
        db.commit()
        return cursor.rowcount > 0


class AnalysisModel:
    """Data access layer for resume-vs-job analysis records."""

    @staticmethod
    def _deserialize_row(row):
        item = dict(row)
        for field in ('matching_skills', 'missing_skills', 'recommendations'):
            try:
                item[field] = json.loads(item[field])
            except Exception:
                item[field] = []
        return item

    @staticmethod
    def save_analysis(
        user_id,
        resume_id,
        job_id,
        match_score,
        resume_score,
        skills_match_score,
        keyword_match_score,
        matching_skills,
        missing_skills,
        recommendations
    ):
        db = get_db()
        cursor = db.cursor()

        matching_str = json.dumps(matching_skills) if isinstance(matching_skills, (list, dict)) else matching_skills
        missing_str = json.dumps(missing_skills) if isinstance(missing_skills, (list, dict)) else missing_skills
        recommendations_str = json.dumps(recommendations) if isinstance(recommendations, (list, dict)) else recommendations

        cursor.execute(
            """INSERT INTO analyses
               (user_id, resume_id, job_id, match_score, resume_score, skills_match_score,
                keyword_match_score, matching_skills, missing_skills, recommendations)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                resume_id,
                job_id,
                float(match_score),
                float(resume_score),
                float(skills_match_score),
                float(keyword_match_score),
                matching_str,
                missing_str,
                recommendations_str,
            )
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_id(analysis_id, user_id=None):
        db = get_db()
        query = """
            SELECT a.*, r.filename, j.title as job_title, j.description as job_description, r.resume_text
            FROM analyses a
            JOIN resumes r ON a.resume_id = r.id
            JOIN jobs j ON a.job_id = j.id
            WHERE a.id = ?
        """
        params = [analysis_id]
        if user_id:
            query += " AND a.user_id = ?"
            params.append(user_id)

        row = db.execute(query, params).fetchone()
        if not row:
            return None
        return AnalysisModel._deserialize_row(row)

    @staticmethod
    def get_user_analyses(user_id):
        db = get_db()
        rows = db.execute(
            """
            SELECT a.*, r.filename, j.title as job_title
            FROM analyses a
            JOIN resumes r ON a.resume_id = r.id
            JOIN jobs j ON a.job_id = j.id
            WHERE a.user_id = ?
            ORDER BY a.created_at DESC
            """,
            (user_id,)
        ).fetchall()
        return [AnalysisModel._deserialize_row(r) for r in rows]

    @staticmethod
    def delete_analysis(analysis_id, user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM analyses WHERE id = ? AND user_id = ?",
            (analysis_id, user_id)
        )
        db.commit()
        return cursor.rowcount > 0
