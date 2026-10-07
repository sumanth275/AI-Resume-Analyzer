import io
from functools import wraps
from flask import session, redirect, url_for, flash, request

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from models.user_model import UserModel

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))

        user = UserModel.get_by_id(session['user_id'])
        if not user:
            session.clear()
            flash('Your session is no longer valid. Please log in again.', 'warning')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function

def generate_pdf_report(analysis):
    """
    Generates a beautifully formatted PDF report of the analysis results
    using ReportLab and returns a BytesIO buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E293B'),
        alignment=0,
        spaceAfter=15
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )

    bullet_style = ParagraphStyle(
        'ReportBullet',
        parent=body_style,
        leftIndent=15,
        spaceAfter=4
    )

    elements = []

    # Title Banner
    elements.append(Paragraph("AI Resume Analyzer & Job Match Report", title_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#4F46E5'), spaceAfter=15))

    # Job & Resume Metadata Table
    job_title = analysis.get('job_title', 'Target Role')
    filename = analysis.get('filename', 'Resume.pdf')
    date_str = str(analysis.get('created_at', ''))[:19]

    meta_data = [
        [Paragraph("<b>Target Job Role:</b>", body_style), Paragraph(job_title, body_style)],
        [Paragraph("<b>Resume File:</b>", body_style), Paragraph(filename, body_style)],
        [Paragraph("<b>Analysis Date:</b>", body_style), Paragraph(date_str, body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[120, 400])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 15))

    # Score Summary Table
    match_score = analysis.get('match_score', 0)
    resume_score = analysis.get('resume_score', 0)
    skills_score = analysis.get('skills_match_score', 0)
    keyword_score = analysis.get('keyword_match_score', 0)

    score_data = [
        [
            Paragraph("<b>Overall Job Match Score</b>", body_style),
            Paragraph(f"<font size=16 color='#4F46E5'><b>{match_score}%</b></font>", body_style)
        ],
        [Paragraph("Resume Quality Score", body_style), Paragraph(f"<b>{resume_score}%</b>", body_style)],
        [Paragraph("Skills Overlap Match", body_style), Paragraph(f"<b>{skills_score}%</b>", body_style)],
        [Paragraph("TF-IDF Keyword Similarity", body_style), Paragraph(f"<b>{keyword_score}%</b>", body_style)]
    ]
    score_table = Table(score_data, colWidths=[260, 260])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EEF2FF')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#FFFFFF')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 15))

    # Matching Skills
    matching_skills = analysis.get('matching_skills', [])
    elements.append(Paragraph("✅ Matching Skills Found in Resume", heading_style))
    if matching_skills:
        skills_text = " • ".join(matching_skills)
        elements.append(Paragraph(skills_text, body_style))
    else:
        elements.append(Paragraph("No direct matching skills detected.", body_style))
    elements.append(Spacer(1, 12))

    # Missing Skills
    missing_skills = analysis.get('missing_skills', [])
    elements.append(Paragraph("❌ Missing Skills Required by Job", heading_style))
    if missing_skills:
        missing_text = " • ".join(missing_skills)
        elements.append(Paragraph(f"<font color='#DC2626'>{missing_text}</font>", body_style))
    else:
        elements.append(Paragraph("<font color='#16A34A'>Great news! No major required skills were missing.</font>", body_style))
    elements.append(Spacer(1, 15))

    # Recommendations
    recommendations = analysis.get('recommendations', [])
    elements.append(Paragraph("💡 AI Recommendations & Next Steps", heading_style))
    if recommendations:
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", bullet_style))
    else:
        elements.append(Paragraph("Your resume is well aligned with this job description.", body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
