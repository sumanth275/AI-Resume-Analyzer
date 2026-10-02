from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user_model import UserModel
from utils.validators import validate_email, validate_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('analysis.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html', name=name, email=email)

        if not validate_email(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html', name=name, email=email)

        if not validate_password(password):
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html', name=name, email=email)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', name=name, email=email)

        existing_user = UserModel.get_by_email(email)
        if existing_user:
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        try:
            user_id = UserModel.create_user(name, email, password)
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            flash(f'Account created successfully! Welcome, {name}.', 'success')
            return redirect(url_for('analysis.dashboard'))
        except Exception as e:
            flash(f'An error occurred during registration: {str(e)}', 'danger')

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('analysis.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html', email=email)

        user = UserModel.get_by_email(email)
        if user and UserModel.verify_password(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash(f'Welcome back, {user["name"]}!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('analysis.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))
