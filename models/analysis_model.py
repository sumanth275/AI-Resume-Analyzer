import json
from database.db import get_db

class ResumeModel:
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
            "SELECT * FROM resumes WHERE user_id = ? ORDER BY uploaded_at DESC", (user_id,)
        ).fetchall()

    @staticmethod
    def get_by_id(resume_id, user_id=None):
        db = get_db()
        if user_id:
            return db.execute(
                "SELECT * FROM resumes WHERE id = ? AND user_id = ?", (resume_id, user_id)
            ).fetchone()
        return db.execute(
            "SELECT * FROM resumes WHERE id = ?", (resume_id,)
        ).fetchone()

    @staticmethod
    def delete_resume(resume_id, user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM resumes WHERE id = ? AND user_id = ?", (resume_id, user_id)
        )
        db.commit()
        return cursor.rowcount > 0


class JobModel:
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
            "SELECT * FROM jobs WHERE id = ?", (job_id,)
        ).fetchone()


class AnalysisModel:
    @staticmethod
    def save_analysis(user_id, resume_id, job_id, match_score, resume_score, 
                      skills_match_score, keyword_match_score, 
                      matching_skills, missing_skills, recommendations):
        db = get_db()
        cursor = db.cursor()
        
        # Serialize lists/dicts to JSON strings if needed
        matching_str = json.dumps(matching_skills) if isinstance(matching_skills, (list, dict)) else matching_skills
        missing_str = json.dumps(missing_skills) if isinstance(missing_skills, (list, dict)) else missing_skills
        recommendations_str = json.dumps(recommendations) if isinstance(recommendations, (list, dict)) else recommendations

        cursor.execute(
            """INSERT INTO analyses 
               (user_id, resume_id, job_id, match_score, resume_score, skills_match_score, 
                keyword_match_score, matching_skills, missing_skills, recommendations) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, resume_id, job_id, float(match_score), float(resume_score),
             float(skills_match_score), float(keyword_match_score),
             matching_str, missing_str, recommendations_str)
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
            
        result = dict(row)
        # Parse JSON fields safely
        try:
            result['matching_skills'] = json.loads(result['matching_skills'])
        except Exception:
            result['matching_skills'] = []
            
        try:
            result['missing_skills'] = json.loads(result['missing_skills'])
        except Exception:
            result['missing_skills'] = []
            
        try:
            result['recommendations'] = json.loads(result['recommendations'])
        except Exception:
            result['recommendations'] = []
            
        return result

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
            """, (user_id,)
        ).fetchall()
        
        results = []
        for r in rows:
            item = dict(r)
            try:
                item['matching_skills'] = json.loads(item['matching_skills'])
            except Exception:
                item['matching_skills'] = []
            try:
                item['missing_skills'] = json.loads(item['missing_skills'])
            except Exception:
                item['missing_skills'] = []
            try:
                item['recommendations'] = json.loads(item['recommendations'])
            except Exception:
                item['recommendations'] = []
            results.append(item)
        return results

    @staticmethod
    def delete_analysis(analysis_id, user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = ? AND user_id = ?", (analysis_id, user_id))
        db.commit()
        return cursor.rowcount > 0
