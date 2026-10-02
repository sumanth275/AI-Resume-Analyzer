import urllib.request
import urllib.parse
import json
import http.cookiejar
import os
import time
import pymupdf

BASE_URL = "http://127.0.0.1:5000"

def test_live_app():
    print("=== LIVE SERVER INTEGRATION TEST ===")
    
    # Cookie jar to maintain session across HTTP requests
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    # 1. Test Home Page
    resp = opener.open(f"{BASE_URL}/")
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert "AI Resume Analyzer" in html
    print("[SUCCESS] 1. Home Page HTTP GET 200 OK")

    # 2. Test User Registration with unique email
    unique_email = f"livetest_{int(time.time())}@example.com"
    reg_data = urllib.parse.urlencode({
        'name': 'Live Test User',
        'email': unique_email,
        'password': 'password123',
        'confirm_password': 'password123'
    }).encode('utf-8')

    req = urllib.request.Request(f"{BASE_URL}/auth/register", data=reg_data, method='POST')
    resp = opener.open(req)
    assert resp.status == 200
    reg_html = resp.read().decode('utf-8')
    assert "Dashboard" in reg_html
    print(f"[SUCCESS] 2. User Registration & Auto-Login ({unique_email}) HTTP 200 OK")

    # 3. Test Dashboard GET
    resp = opener.open(f"{BASE_URL}/dashboard")
    dash_html = resp.read().decode('utf-8')
    assert "Dashboard" in dash_html
    print("[SUCCESS] 3. Dashboard HTTP GET 200 OK")

    # 4. Create sample PDF resume to upload
    sample_pdf_path = os.path.join(os.path.dirname(__file__), "live_test_resume.pdf")
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((40, 40), """
    ALEXANDER SMITH
    Email: alex.smith@example.com | Phone: 555-123-4567 | Portfolio: github.com/alexsmith
    
    SUMMARY
    Senior Full-Stack Engineer with experience in Python, Flask, React, SQL, and Docker.
    
    EXPERIENCE
    Lead Developer at WebTech Corp
    - Engineered Flask microservices handling 100k requests/day.
    - Optimized SQL queries and database indexes, reducing latency by 45%.
    - Built frontend dashboards using React, JavaScript, and CSS.
    
    SKILLS
    Python, Flask, Django, SQL, PostgreSQL, SQLite, React, JavaScript, HTML, CSS, Docker, Git, CI/CD
    
    EDUCATION
    B.S. Software Engineering - Tech University
    """, fontsize=10)
    doc.save(sample_pdf_path)
    doc.close()

    # 5. Upload Resume & Analyze against Job Description using multipart/form-data
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    job_title = "Senior Python Flask Developer"
    job_desc = "We need a Senior Python Developer skilled in Flask, SQL, PostgreSQL, Docker, AWS, Kubernetes, Git, and React."

    body_parts = []
    
    # job_title
    body_parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"job_title\"\r\n\r\n{job_title}\r\n".encode('utf-8'))
    # job_description
    body_parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"job_description\"\r\n\r\n{job_desc}\r\n".encode('utf-8'))
    # resume_source
    body_parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"resume_source\"\r\n\r\nnew\r\n".encode('utf-8'))
    
    # resume_file
    with open(sample_pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    file_header = f"--{boundary}\r\nContent-Disposition: form-data; name=\"resume_file\"; filename=\"live_test_resume.pdf\"\r\nContent-Type: application/pdf\r\n\r\n".encode('utf-8')
    body_parts.append(file_header + pdf_bytes + b"\r\n")
    body_parts.append(f"--{boundary}--\r\n".encode('utf-8'))

    full_body = b"".join(body_parts)

    req = urllib.request.Request(
        f"{BASE_URL}/analyze",
        data=full_body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method='POST'
    )

    resp = opener.open(req)
    result_html = resp.read().decode('utf-8')
    assert "Match Analysis Results" in result_html or "JOB MATCH SCORE" in result_html
    print("[SUCCESS] 4. Resume Upload & Job Match Analysis HTTP 200 OK")

    # 6. Test PDF Report Download HTTP Endpoint
    download_url = f"{BASE_URL}/download-report/2"
    resp = opener.open(download_url)
    assert resp.status == 200
    assert resp.headers.get('Content-Type') == 'application/pdf'
    pdf_report_bytes = resp.read()
    assert len(pdf_report_bytes) > 500
    print("[SUCCESS] 5. PDF Report Download HTTP 200 OK (Report size: {} bytes)".format(len(pdf_report_bytes)))

    # Cleanup sample pdf
    if os.path.exists(sample_pdf_path):
        os.remove(sample_pdf_path)

    print("\n[SUCCESS] ALL LIVE SERVER TESTS PASSED 100%! Application is fully functional.")

if __name__ == '__main__':
    test_live_app()
