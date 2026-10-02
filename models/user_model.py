from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db

class UserModel:
    @staticmethod
    def create_user(name, email, password):
        db = get_db()
        hashed_pw = generate_password_hash(password)
        try:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email.strip().lower(), hashed_pw)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def get_by_email(email):
        db = get_db()
        return db.execute(
            "SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),)
        ).fetchone()

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        return db.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()

    @staticmethod
    def verify_password(stored_password_hash, password):
        return check_password_hash(stored_password_hash, password)
