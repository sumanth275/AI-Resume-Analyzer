
import os
from flask import Flask, render_template, redirect, url_for, session
from config import Config
from db import init_db, close_db, seed_default_jobs_if_needed
from routes.auth_routes import auth_bp
from routes.resume_routes import resume_bp
from routes.analysis_routes import analysis_bp
from routes.job_routes import job_bp
from routes.application_routes import application_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure required runtime directories exist
    if app.config.get('UPLOAD_FOLDER'):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    if app.config.get('REPORTS_FOLDER'):
        os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

    # Initialize Database Schema
    with app.app_context():
        init_db(app)
        if not app.config.get('TESTING'):
            seed_default_jobs_if_needed(app)

    # Database connection teardown
    app.teardown_appcontext(close_db)

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(resume_bp, url_prefix='/resume')
    app.register_blueprint(analysis_bp, url_prefix='/')
    app.register_blueprint(job_bp, url_prefix='/jobs')
    app.register_blueprint(application_bp, url_prefix='/')

    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('analysis.dashboard'))
        return render_template('index.html')

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template(
            'base.html',
            content_override="<div class='container my-5 text-center'><h2>404 - Page Not Found</h2><p>The page you requested does not exist.</p><a href='/' class='btn btn-primary mt-3'>Back to Home</a></div>"
        ), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template(
            'base.html',
            content_override="<div class='container my-5 text-center'><h2>500 - Internal Server Error</h2><p>Something went wrong on our servers.</p><a href='/' class='btn btn-primary mt-3'>Back to Home</a></div>"
        ), 500

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return render_template(
            'base.html',
            content_override="<div class='container my-5 text-center'><h2>413 - File Too Large</h2><p>The uploaded PDF exceeds the 16MB limit.</p><a href='/analyze-page' class='btn btn-primary mt-3'>Try Again</a></div>"
        ), 413

    return app


app = create_app()


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    )
