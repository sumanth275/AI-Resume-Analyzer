import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pymupdf
from services.pdf_parser import extract_text_from_pdf
from services.skill_extractor import extract_skills
from services.job_matcher import calculate_job_match
from utils.helpers import generate_pdf_report

def run_simulation():
    print("=== AI Resume Analyzer End-to-End Simulation ===")
    
    # 1. Generate Sample PDF Resume
    pdf_path = os.path.join(os.path.dirname(__file__), "sample_python_dev_resume.pdf")
    doc = pymupdf.open()
    page = doc.new_page()
    sample_resume_content = """
    ALEX JOHNSON
    Email: alex.johnson@example.com | Phone: (555) 234-5678 | Portfolio: github.com/alexjohnson

    PROFESSIONAL SUMMARY
    Senior Software Engineer with 4+ years of experience designing and deploying web applications and machine learning models.

    TECHNICAL SKILLS
    - Languages: Python, JavaScript, SQL, HTML, CSS, C++
    - Frameworks: Flask, Django, React, FastAPI
    - Databases: PostgreSQL, SQLite, Redis
    - Machine Learning: Scikit-learn, Pandas, NumPy, TensorFlow, NLP
    - DevOps & Tools: Git, GitHub, Linux, CI/CD

    WORK EXPERIENCE
    Software Engineer | TechInnovate Solutions (2022 - Present)
    - Developed REST APIs using Flask and PostgreSQL serving 50,000+ daily active users.
    - Built automated text processing pipeline using TF-IDF and Cosine Similarity, improving search accuracy by 35%.
    - Managed version control and CI/CD pipelines with GitHub Actions.

    EDUCATION
    B.S. in Computer Science | University of Technology (2018 - 2022)
    """
    page.insert_text((40, 40), sample_resume_content, fontsize=10)
    doc.save(pdf_path)
    doc.close()
    print(f"[SUCCESS] Created sample PDF resume at: {pdf_path}")

    # 2. Extract Text using PyMuPDF
    extracted_text = extract_text_from_pdf(pdf_path)
    print(f"[SUCCESS] Extracted {len(extracted_text.split())} words from PDF using PyMuPDF.")

    # 3. Sample Job Description
    job_description = """
    We are looking for a Senior Full-Stack Python Developer to join our engineering team.
    Requirements:
    - 3+ years experience with Python and web frameworks (Flask or Django).
    - Strong database skills in SQL (PostgreSQL, SQLite).
    - Experience with Machine Learning, Scikit-learn, Pandas, and NLP is a huge plus.
    - Familiarity with frontend frameworks like React or Vue.js.
    - Required Cloud & DevOps: Docker, AWS, Kubernetes, Git, CI/CD.
    """

    # 4. Run NLP / ML Job Matching Engine
    match_results = calculate_job_match(extracted_text, job_description)

    print("\n--- MATCHING RESULTS ---")
    print(f"Overall Job Match Score : {match_results['match_score']}%")
    print(f"Resume Structural Score  : {match_results['resume_score']}%")
    print(f"Skills Overlap Score    : {match_results['skills_match_score']}%")
    print(f"TF-IDF Keyword Match    : {match_results['keyword_match_score']}%")
    print(f"Matching Skills          : {', '.join(match_results['matching_skills'])}")
    print(f"Missing Skills           : {', '.join(match_results['missing_skills'])}")
    print("Recommendations:")
    for rec in match_results['recommendations']:
        print(f"   * {rec}")

    # 5. Test PDF Report Generation
    mock_analysis_data = {
        'id': 101,
        'job_title': 'Senior Full-Stack Python Developer',
        'filename': 'sample_python_dev_resume.pdf',
        'created_at': '2026-10-02 11:00:00',
        'match_score': match_results['match_score'],
        'resume_score': match_results['resume_score'],
        'skills_match_score': match_results['skills_match_score'],
        'keyword_match_score': match_results['keyword_match_score'],
        'matching_skills': match_results['matching_skills'],
        'missing_skills': match_results['missing_skills'],
        'recommendations': match_results['recommendations']
    }

    report_buffer = generate_pdf_report(mock_analysis_data)
    report_output_path = os.path.join(os.path.dirname(__file__), "Generated_Match_Report.pdf")
    with open(report_output_path, "wb") as f:
        f.write(report_buffer.read())

    print(f"\n[SUCCESS] ReportLab PDF Report successfully generated at: {report_output_path}")

    # Cleanup temporary PDF files
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    if os.path.exists(report_output_path):
        os.remove(report_output_path)

    print("\n[SUCCESS] End-to-End Simulation completed successfully with 100% pass!")

if __name__ == '__main__':
    run_simulation()
