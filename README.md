# 🤖 AI Resume Analyzer & Job Matcher

A full-stack Web Application built with **Python, Flask, PyMuPDF, Scikit-learn, and SQLite** that automatically analyzes resume PDFs against job descriptions using Natural Language Processing (NLP), TF-IDF vectorization, Cosine Similarity, and intelligent skill extraction.

---

## 🌟 Key Features

- 📄 **PyMuPDF PDF Text Extraction**: Extracts clean text from uploaded PDF resumes.
- 🧠 **NLP & TF-IDF Cosine Match Engine**: Vectorizes resume and job description text to calculate exact keyword similarity percentages.
- 🎯 **Skill Extraction & Gap Analysis**: Detects matching technical skills and pinpoints missing job requirements.
- 📊 **Interactive Result Dashboard**: Visual gauge display, progress bars, breakdown scorecards (Resume Quality, Skill Match, Keyword Match), matching/missing skill tags, and actionable recommendations.
- 📥 **PDF Report Download**: Generates downloadable PDF match analysis reports powered by ReportLab.
- 🔐 **User Authentication**: Secure user registration, password hashing (Werkzeug), and session management.
- 💾 **SQLite Database**: Persistent relational database for user profiles, uploaded resumes, job listings, and historical analysis reports.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript, Font Awesome, Google Fonts |
| **Backend** | Python 3.14+, Flask 3.1+ |
| **PDF Processing** | PyMuPDF (`fitz`) |
| **NLP & ML** | Scikit-learn (`TfidfVectorizer`, `cosine_similarity`), NumPy |
| **PDF Report Generation** | ReportLab |
| **Database** | SQLite3 |
| **Testing** | PyTest |

---

## 📁 Project Structure

```text
AI-Resume-Analyzer/
├── app.py                         ← Main Flask application entry point
├── config.py                      ← App configurations
├── requirements.txt               ← Python package dependencies
├── README.md                      ← Documentation
├── .gitignore                     ← Git ignore rules
│
├── database/
│   ├── database.db                ← SQLite database file (generated at runtime)
│   └── db.py                      ← Database connection & schema initialization
│
├── models/
│   ├── user_model.py              ← User database operations & authentication
│   └── analysis_model.py          ← Resume, Job, and Analysis database models
│
├── routes/
│   ├── auth_routes.py             ← User registration, login, logout routes
│   ├── resume_routes.py           ← PDF upload and resume management routes
│   └── analysis_routes.py         ← Analysis execution, result dashboard, report download
│
├── services/
│   ├── pdf_parser.py              ← PDF to text extraction using PyMuPDF
│   ├── text_processor.py          ← Text cleaning, tokenization, stopword removal
│   ├── skill_extractor.py         ← Skill taxonomy & boundary regex skill extraction
│   ├── resume_analyzer.py         ← Standalone structural resume scoring
│   └── job_matcher.py             ← TF-IDF + Cosine Similarity matching engine
│
├── templates/
│   ├── base.html                  ← Layout template with navbar, flash alerts, and footer
│   ├── index.html                 ← Home landing page
│   ├── login.html                 ← User login page
│   ├── register.html              ← Registration page
│   ├── dashboard.html             ← User dashboard with stats & history table
│   ├── upload.html                ← Resume upload & job description matching form
│   └── result.html                ← Interactive result dashboard
│
├── static/
│   ├── css/
│   │   ├── style.css              ← Main application styles & theme
│   │   ├── dashboard.css          ← Dashboard & upload form styles
│   │   └── result.css             ← Result gauge, progress bar, & pill styles
│   │
│   ├── js/
│   │   ├── main.js                ← Flash message auto-dismiss
│   │   ├── upload.js              ← Drag & drop PDF file upload logic
│   │   └── result.js              ← Animated score counter
│   │
│   └── images/
│
├── uploads/
│   └── .gitkeep                   ← Uploaded PDF storage folder
│
├── utils/
│   ├── helpers.py                 ← Login decorator & ReportLab PDF report generator
│   └── validators.py              ← File extension & input validation helpers
│
└── tests/
    ├── test_pdf_parser.py         ← Unit tests for PDF parser
    ├── test_matcher.py            ← Unit tests for NLP engine & skill extraction
    └── test_routes.py             ← Integration tests for Flask routes
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your system.

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Run the Flask Application
```bash
python app.py
```
The application will launch on `http://127.0.0.1:5000`.

### 4. Run Tests
```bash
python -m pytest tests/
```

---

## 🚀 Data Flow & Architecture

```text
Resume PDF
    ↓
PyMuPDF (fitz)
    ↓
Extract Raw Text
    ↓
Text Cleaning & Preprocessing
    ↓
Skill Extraction Engine
    ↓
┌──────────────────────────────────────┐
│       TF-IDF Vectorizer Engine       │
└──────────────────┬───────────────────┘
                   ↓
           Cosine Similarity
                   ↓
         Overall Job Match Score
                   ↓
  ┌────────────────┼────────────────┐
  ↓                ↓                ↓
Match Skills   Missing Skills   Resume Score
  │                │                │
  └────────────────┼────────────────┘
                   ↓
            Recommendations
                   ↓
             SQLite Storage
                   ↓
           Flask API Response
                   ↓
           Web Result Dashboard & PDF Report
```
