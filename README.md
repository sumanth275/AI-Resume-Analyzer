# AI Resume Analyzer & Job Matcher

A full-stack web application built with Python and Flask that analyzes PDF resumes against job descriptions, calculates job-match scores, identifies matching and missing skills, and helps job seekers discover and track job opportunities.

## Project Overview

AI Resume Analyzer helps job seekers understand how well their resumes match specific job requirements.

The application extracts text from PDF resumes, processes the content using NLP techniques, identifies relevant skills, and compares resumes with job descriptions using TF-IDF and Cosine Similarity.

Users can also manage their resume history, explore job opportunities, track applications, and download PDF analysis reports.

## Features

### Resume Analysis
- Upload PDF resumes.
- Extract text from PDF documents.
- Clean and preprocess resume content.
- Identify technical skills.
- Analyze resume structure.
- Calculate resume and job-match scores.
- Identify matching and missing skills.
- Generate personalized recommendations.

### Job Portal
- Explore job opportunities.
- Search and filter job listings.
- View recommended jobs.
- Apply for available jobs.
- Track application status.
- Support internal and external job applications.
- Admin job-listing management.

### User Dashboard
- User registration and login.
- Password hashing.
- Resume analysis history.
- Resume history management.
- Dashboard summary cards.
- Downloadable PDF reports.
- Responsive user interface.

## Technologies Used

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite |
| PDF Processing | PyMuPDF |
| Machine Learning | Scikit-learn |
| Numerical Processing | NumPy |
| Text Analysis | TF-IDF, Cosine Similarity |
| PDF Reports | ReportLab |
| Testing | Pytest |
| Deployment Server | Gunicorn |
| Hosting | Render |

## System Architecture

```text
              USER
                |
                v
        PDF Resume Upload
                |
                v
        FLASK APPLICATION
                |
        +-------+--------+
        |                |
        v                v
   PDF Extraction    Job Description
        |                |
        +-------+--------+
                |
                v
       Text Preprocessing
                |
                v
        Skill Extraction
                |
                v
         TF-IDF Analysis
                |
                v
       Cosine Similarity
                |
                v
        Job Match Analysis
                |
        +-------+--------+
        |        |       |
        v        v       v
     Matching Missing  Match
      Skills  Skills   Score
        |        |       |
        +--------+-------+
                |
                v
        Recommendations
                |
                v
         SQLite Database
                |
                v
         User Dashboard
                |
                v
           PDF Report
```

## Project Structure

```text
AI-Resume-Analyzer/
|
|-- app.py
|-- config.py
|-- db.py
|-- requirements.txt
|-- README.md
|
|-- database/
|   |-- db.py
|
|-- models/
|   |-- user_model.py
|   |-- resume_model.py
|   |-- job_model.py
|   |-- application_model.py
|   |-- analysis_model.py
|   |-- job_portal_model.py
|
|-- routes/
|   |-- auth_routes.py
|   |-- resume_routes.py
|   |-- analysis_routes.py
|   |-- job_routes.py
|   |-- application_routes.py
|
|-- services/
|   |-- job_matcher.py
|   |-- resume_analyzer.py
|   |-- auto_apply_engine.py
|   |-- recommendation_engine.py
|
|-- templates/
|-- static/
|-- uploads/
|-- reports/
|-- tests/
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sumanth275/AI-Resume-Analyzer.git
```

### 2. Navigate to the Project

```bash
cd AI-Resume-Analyzer
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python app.py
```

Open your browser:

```text
http://127.0.0.1:5000
```

## Run Tests

Execute the automated test suite:

```bash
python -B -m pytest --ignore=tests/live_server_test.py -v
```

The project currently passes 35 tests with this command.

## Environment Variables

Configure these environment variables for deployment:

| Variable | Purpose |
|---|---|
| SECRET_KEY | Secure Flask session signing key |
| PORT | Application server port |
| FLASK_DEBUG | Enable or disable debug mode |

For production, set a strong, randomly generated `SECRET_KEY`. Never commit real secrets to GitHub.

## Deployment on Render

Create a new Web Service and connect this GitHub repository.

Use these settings:

**Build Command**

```bash
pip install -r requirements.txt
```

**Start Command**

```bash
gunicorn app:app
```

Set the following environment variables in Render:

```text
SECRET_KEY = your-generated-random-secret
FLASK_DEBUG = false
```

Render provides the `PORT` variable automatically.

**Important:** This application currently uses SQLite and local folders for uploaded resumes and generated reports. Render's ordinary ephemeral filesystem does not guarantee permanent storage. Configure persistent storage or migrate to managed database and file storage before relying on production user data.

## Future Enhancements

- Cloud-based resume storage.
- PostgreSQL database integration.
- Advanced NLP-based resume analysis.
- More personalized job recommendations.
- Improved analytics dashboard.
- Email notifications for application updates.
- Enhanced security and deployment monitoring.

## Author

**Sumanth Yerukula**

GitHub: https://github.com/sumanth275

LinkedIn: https://www.linkedin.com/in/sake-sumanth-932645299

## License

This project is developed for educational and portfolio purposes.
