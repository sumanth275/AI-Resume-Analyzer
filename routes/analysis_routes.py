import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_file, jsonify

from models.analysis_model import ResumeModel, JobModel, AnalysisModel
from services.pdf_parser import extract_text_from_pdf
from services.job_matcher import calculate_job_match
from utils.validators import allowed_file
from utils.helpers import login_required, generate_pdf_report

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    resumes = ResumeModel.get_by_user(user_id)
    analyses = AnalysisModel.get_user_analyses(user_id)
    
    # Calculate stats for summary cards
    total_resumes = len(resumes)
    total_analyses = len(analyses)
    avg_match_score = round(sum(a['match_score'] for a in analyses) / total_analyses, 1) if total_analyses > 0 else 0.0

    return render_template(
        'dashboard.html', 
        resumes=resumes, 
        analyses=analyses,
        total_resumes=total_resumes,
        total_analyses=total_analyses,
        avg_match_score=avg_match_score
    )


@analysis_bp.route('/analyze-page', methods=['GET'])
@login_required
def upload_page():
    user_id = session['user_id']
    resumes = ResumeModel.get_by_user(user_id)
    selected_resume_id = request.args.get('selected_resume', type=int)
    return render_template('upload.html', resumes=resumes, selected_resume_id=selected_resume_id)


@analysis_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    user_id = session['user_id']
    
    job_title = request.form.get('job_title', '').strip() or 'Target Job Role'
    job_description = request.form.get('job_description', '').strip()
    resume_source = request.form.get('resume_source', 'new')  # 'existing' or 'new'
    existing_resume_id = request.form.get('existing_resume_id', type=int)

    if not job_description:
        flash('Please provide a job description for analysis.', 'danger')
        return redirect(url_for('analysis.upload_page'))

    resume_text = ""
    resume_id = None

    if resume_source == 'existing' and existing_resume_id:
        resume = ResumeModel.get_by_id(existing_resume_id, user_id)
        if not resume:
            flash('Selected resume not found.', 'danger')
            return redirect(url_for('analysis.upload_page'))
        resume_text = resume['resume_text']
        resume_id = resume['id']
    else:
        # Handle new PDF upload
        if 'resume_file' not in request.files:
            flash('Please select a resume PDF file to upload.', 'danger')
            return redirect(url_for('analysis.upload_page'))
            
        file = request.files['resume_file']
        if file.filename == '':
            flash('No file selected for upload.', 'danger')
            return redirect(url_for('analysis.upload_page'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            
            saved_filename = f"user_{user_id}_{filename}"
            filepath = os.path.join(upload_dir, saved_filename)
            file.save(filepath)

            try:
                resume_text = extract_text_from_pdf(filepath)
                resume_id = ResumeModel.save_resume(user_id, filename, filepath, resume_text)
            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash(f'Failed to process PDF resume: {str(e)}', 'danger')
                return redirect(url_for('analysis.upload_page'))
        else:
            flash('Invalid file format. Only PDF files are supported.', 'danger')
            return redirect(url_for('analysis.upload_page'))

    # Save Job record
    job_id = JobModel.save_job(user_id, job_title, job_description)

    # Run ML / NLP Analysis Pipeline
    results = calculate_job_match(resume_text, job_description)

    # Save Analysis to Database
    analysis_id = AnalysisModel.save_analysis(
        user_id=user_id,
        resume_id=resume_id,
        job_id=job_id,
        match_score=results['match_score'],
        resume_score=results['resume_score'],
        skills_match_score=results['skills_match_score'],
        keyword_match_score=results['keyword_match_score'],
        matching_skills=results['matching_skills'],
        missing_skills=results['missing_skills'],
        recommendations=results['recommendations']
    )

    flash('Analysis completed successfully!', 'success')
    return redirect(url_for('analysis.result', analysis_id=analysis_id))


@analysis_bp.route('/result/<int:analysis_id>')
@login_required
def result(analysis_id):
    user_id = session['user_id']
    analysis = AnalysisModel.get_by_id(analysis_id, user_id)
    if not analysis:
        flash('Analysis report not found.', 'danger')
        return redirect(url_for('analysis.dashboard'))

    return render_template('result.html', analysis=analysis)


@analysis_bp.route('/download-report/<int:analysis_id>')
@login_required
def download_report(analysis_id):
    user_id = session['user_id']
    analysis = AnalysisModel.get_by_id(analysis_id, user_id)
    if not analysis:
        flash('Analysis report not found.', 'danger')
        return redirect(url_for('analysis.dashboard'))

    pdf_buffer = generate_pdf_report(analysis)
    report_filename = f"Resume_Analysis_Report_{analysis_id}.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=report_filename,
        mimetype='application/pdf'
    )


@analysis_bp.route('/delete-analysis/<int:analysis_id>', methods=['POST'])
@login_required
def delete_analysis(analysis_id):
    user_id = session['user_id']
    success = AnalysisModel.delete_analysis(analysis_id, user_id)
    if success:
        flash('Analysis record deleted.', 'info')
    else:
        flash('Could not delete analysis record.', 'danger')
    return redirect(url_for('analysis.dashboard'))
