import re
from flask import current_app

def allowed_file(filename):
    """
    Checks if the uploaded file has a permitted extension (.pdf).
    """
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']

def validate_email(email):
    """
    Basic email format validation.
    """
    if not email or len(email) > 255:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """
    Validates password strength (at least 6 chars).
    """
    return bool(password and len(password) >= 6)
