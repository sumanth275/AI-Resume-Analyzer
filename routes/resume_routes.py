import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify

from models.analysis_model import ResumeModel
from services.pdf_parser import extract_text_from_pdf
from utils.validators import allowed_file
from utils.helpers import login_required

resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    user_id = session['user_id']
    
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)
            
        file = request.files['resume']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            
            # Append user_id prefix to prevent name collisions
            saved_filename = f"user_{user_id}_{filename}"
            filepath = os.path.join(upload_dir, saved_filename)
            file.save(filepath)

            try:
                # Extract text using PyMuPDF service
                resume_text = extract_text_from_pdf(filepath)
                
                # Save to database
                resume_id = ResumeModel.save_resume(user_id, filename, filepath, resume_text)
                
                flash(f'Resume "{filename}" uploaded and parsed successfully!', 'success')
                
                # If AJAX request, return JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': True,
                        'resume_id': resume_id,
                        'filename': filename,
                        'message': 'Resume uploaded successfully'
                    })
                    
                return redirect(url_for('analysis.upload_page', selected_resume=resume_id))

            except Exception as e:
                # Remove saved file on parsing error
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash(f'Error processing PDF: {str(e)}', 'danger')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': str(e)}), 400
                    
                return redirect(request.url)
        else:
            flash('Invalid file type. Only PDF files are supported.', 'danger')
            return redirect(request.url)

    # GET request - list existing uploaded resumes
    user_resumes = ResumeModel.get_by_user(user_id)
    return render_template('upload.html', resumes=user_resumes)


@resume_bp.route('/delete-resume/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    user_id = session['user_id']
    resume = ResumeModel.get_by_id(resume_id, user_id)
    if resume:
        # Delete file from disk if exists
        if os.path.exists(resume['filepath']):
            try:
                os.remove(resume['filepath'])
            except Exception:
                pass
        ResumeModel.delete_resume(resume_id, user_id)
        flash('Resume deleted successfully.', 'info')
    else:
        flash('Resume not found or unauthorized.', 'danger')
        
    return redirect(url_for('analysis.dashboard'))
