# AI Resume Analyzer

A web-based Resume Analyzer built with Python and Flask that analyzes resumes against a job description and provides a job-match score, matching skills, missing skills, and personalized recommendations.

## 🚀 Project Overview

The AI Resume Analyzer helps job seekers understand how well their resume matches a particular job description.

The application extracts text from PDF resumes, processes the text using NLP techniques, identifies relevant skills, and compares the resume with a job description using TF-IDF and Cosine Similarity.

It also provides a dashboard where users can view their analysis history and download a PDF report.

## ✨ Features

- PDF resume upload
- Resume text extraction
- Text cleaning and preprocessing
- Automatic skill extraction
- TF-IDF based text analysis
- Cosine similarity based job matching
- Matching skills detection
- Missing skills detection
- Resume/job match score
- Personalized recommendations
- User registration and login
- Password hashing
- Analysis history
- SQLite database
- PDF analysis report generation
- Responsive web interface
- Automated testing

## 🏗️ System Architecture

```text
                User
                  |
                  v
          Resume PDF Upload
                  |
                  v
        +--------------------+
        |   Flask Backend    |
        +--------------------+
                  |
        +---------+---------+
        |                   |
        v                   v
 PDF Text Extraction   Job Description
        |                   |
        +---------+---------+
                  |
                  v
        Text Preprocessing
                  |
                  v
          Skill Extraction
                  |
                  v
           TF-IDF Vectorizer
                  |
                  v
          Cosine Similarity
                  |
                  v
          Job Match Analysis
                  |
        +---------+---------+
        |         |         |
        v         v         v
   Matching    Missing    Match
    Skills     Skills     Score
        |         |         |
        +---------+---------+
                  |
                  v
          Recommendations
                  |
                  v
           SQLite Storage
                  |
                  v
          Result Dashboard
                  |
                  v
             PDF Report