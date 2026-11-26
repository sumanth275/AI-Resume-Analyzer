import os
import sqlite3
from flask import g, current_app


def get_db():
    """Return a request-scoped SQLite connection with foreign keys enabled."""
    if 'db' not in g:
        db_path = current_app.config['DATABASE_PATH']
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


def close_db(e=None):
    """Close the request-scoped SQLite connection if open."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app=None):
    """Initialize all database tables and apply safe schema migrations."""
    if app:
        db_path = app.config['DATABASE_PATH']
    else:
        db_path = current_app.config['DATABASE_PATH']

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        resume_text TEXT NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        resume_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        match_score REAL NOT NULL,
        resume_score REAL NOT NULL,
        skills_match_score REAL NOT NULL,
        keyword_match_score REAL NOT NULL,
        matching_skills TEXT NOT NULL,
        missing_skills TEXT NOT NULL,
        recommendations TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE,
        FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS job_listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT,
        description TEXT NOT NULL,
        required_skills TEXT,
        application_type TEXT NOT NULL DEFAULT 'internal' CHECK (application_type IN ('internal', 'external')),
        application_url TEXT,
        is_active INTEGER DEFAULT 1,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS job_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_listing_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        resume_id INTEGER,
        cover_letter TEXT,
        status TEXT DEFAULT 'pending',
        match_score REAL DEFAULT 0.0,
        is_auto_applied INTEGER DEFAULT 0,
        notes TEXT,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_listing_id) REFERENCES job_listings (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE SET NULL,
        UNIQUE (job_listing_id, user_id)
    );

    CREATE TABLE IF NOT EXISTS auto_apply_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        resume_id INTEGER,
        min_match_score REAL NOT NULL DEFAULT 60.0,
        location_filter TEXT,
        max_applications INTEGER NOT NULL DEFAULT 5,
        jobs_evaluated INTEGER NOT NULL DEFAULT 0,
        applications_submitted INTEGER NOT NULL DEFAULT 0,
        skipped_count INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE SET NULL
    );
    """)

    # Safe migration: ensure is_admin column exists on users
    cursor.execute("PRAGMA table_info(users);")
    user_cols = [col[1] for col in cursor.fetchall()]
    if 'is_admin' not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0;")
        cursor.execute("UPDATE users SET is_admin = 1 WHERE email = 'suman98@gmail.com' OR id = 1;")

    # Safe migration: ensure auto-apply metadata columns exist on job_applications
    cursor.execute("PRAGMA table_info(job_applications);")
    app_cols = [col[1] for col in cursor.fetchall()]
    if 'match_score' not in app_cols:
        cursor.execute("ALTER TABLE job_applications ADD COLUMN match_score REAL DEFAULT 0.0;")
    if 'is_auto_applied' not in app_cols:
        cursor.execute("ALTER TABLE job_applications ADD COLUMN is_auto_applied INTEGER DEFAULT 0;")
    if 'notes' not in app_cols:
        cursor.execute("ALTER TABLE job_applications ADD COLUMN notes TEXT;")

    conn.commit()
    conn.close()


def seed_default_jobs_if_needed(app=None):
    """
    Seeds at least 20 active job listings across diverse tech domains if fewer than 20 exist.
    """
    if app:
        db_path = app.config['DATABASE_PATH']
    else:
        db_path = current_app.config['DATABASE_PATH']

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM job_listings;")
    count = cursor.fetchone()[0]

    if count < 20:
        seed_jobs = [
            ("Python Developer", "Infosys Technologies", "Bangalore, India", "Seeking a skilled Python developer to develop scalable microservices, REST APIs, and database schemas using Flask, Django, and SQL in Bangalore tech hub.", "Python, Flask, Django, FastAPI, SQL, Git, REST API, Databases", "internal", None),
            ("AI Engineer", "Microsoft India", "Hyderabad, India", "Exciting opportunity to design Generative AI solutions, LLM pipelines, and deep neural architectures using PyTorch and Python at Microsoft Hyderabad.", "Python, Generative AI, LLM, Deep Learning, PyTorch, TensorFlow, NLP, Machine Learning", "internal", None),
            ("Backend Developer", "Amazon India", "Hyderabad, India", "Build high-throughput payment APIs and backend infrastructure with Python, Node.js, PostgreSQL, Redis, and Docker at Amazon Hyderabad Campus.", "Python, Node.js, Express.js, Flask, SQL, REST API, PostgreSQL, Docker", "internal", None),
            ("Full Stack Developer", "Flipkart", "Bangalore, India", "Looking for versatile Full Stack developers proficient in React, JavaScript, Node.js, Python, and SQL databases for Bangalore team.", "HTML, CSS, JavaScript, React, Node.js, Python, Flask, SQL, REST API, Git", "internal", None),
            ("Machine Learning Engineer", "Google India", "Bangalore, India", "Train, optimize, and deploy cutting-edge ML models into production using Python, Scikit-learn, TensorFlow, and PyTorch at Google Bangalore.", "Python, Machine Learning, Deep Learning, Scikit-learn, TensorFlow, PyTorch, Pandas, SQL", "internal", None),
            ("Data Scientist", "Meta India", "Hyderabad, India", "Analyze large-scale behavioral data, develop predictive models, and design statistical experiments using Python, Pandas, and SQL at Meta Hyderabad.", "Python, Machine Learning, Statistics, Data Science, Pandas, NumPy, Scikit-learn, SQL", "internal", None),
            ("Data Analyst", "Uber India", "Hyderabad, India", "Transform raw business metrics into actionable intelligence with SQL, Excel, Pandas, and data visualization dashboards at Uber Hyderabad Center.", "Python, SQL, Excel, Pandas, NumPy, Data Analysis, Data Analytics, Statistics, Data Visualization", "internal", None),
            ("Frontend Developer", "Swiggy", "Bangalore, India", "Craft responsive, lightning-fast streaming user interfaces using modern React, TypeScript, HTML5, CSS3, and Tailwind at Swiggy Bangalore HQ.", "HTML, CSS, JavaScript, TypeScript, React, Tailwind, Responsive Web Development, REST API", "internal", None),
            ("DevOps Engineer", "ServiceNow", "Hyderabad, India", "Manage CI/CD release pipelines, Kubernetes clusters, Docker containers, and cloud infrastructure at ServiceNow Hyderabad.", "Docker, Kubernetes, CI/CD, Jenkins, Terraform, AWS, Linux, Bash, Git", "internal", None),
            ("Cloud Engineer", "Oracle Cloud", "Bangalore, India", "Design resilient, multi-region cloud architectures across AWS, Azure, and OCI with Terraform, Docker, and Linux in Bangalore.", "AWS, Azure, GCP, Cloud Infrastructure, Terraform, Docker, Kubernetes, Linux", "internal", None),
            ("Data Engineer", "PhonePe", "Bangalore, India", "Construct robust ETL data pipelines and distributed data warehouses with PySpark, Spark, SQL, and Airflow at PhonePe Bangalore.", "Python, SQL, Spark, PySpark, Hadoop, ETL, PostgreSQL, Snowflake, BigQuery", "internal", None),
            ("Software Engineer", "Qualcomm India", "Hyderabad, India", "Solve foundational software engineering challenges focusing on object-oriented architecture, algorithms, and data structures at Qualcomm Hyderabad.", "Python, Java, C++, Object-Oriented Programming, Data Structures, Algorithms, SQL, Git", "internal", None),
            ("NLP Engineer", "Wipro AI Labs", "Bangalore, India", "Advance natural language understanding and generation using Transformers, Hugging Face, BERT, and PyTorch in Bangalore Innovation Labs.", "Python, NLP, Natural Language Processing, Transformers, LLM, Deep Learning, PyTorch", "internal", None),
            ("Computer Vision Engineer", "Ola Electric", "Bangalore, India", "Develop real-time object detection and video processing systems using OpenCV, PyTorch, CNNs, and Python/C++ at Ola Electric Bangalore.", "Python, Computer Vision, OpenCV, Deep Learning, PyTorch, TensorFlow, C++, Machine Learning", "internal", None),
            ("Cyber Security Analyst", "Deloitte Cyber", "Hyderabad, India", "Conduct vulnerability assessments, network penetration testing, and incident investigations in Linux environments at Deloitte Hyderabad.", "Linux, Network Security, Cyber Security, Bash, Shell, Ethical Hacking, Penetration Testing", "internal", None),
            ("Database Administrator", "Salesforce India", "Hyderabad, India", "Manage mission-critical relational databases, indexing strategies, and query performance with PostgreSQL and SQL at Salesforce Hyderabad.", "SQL, PostgreSQL, MySQL, Oracle, Databases, Database Design, Performance Tuning, Indexing", "internal", None),
            ("Mobile App Developer", "Zomato", "Bangalore, India", "Create fluid iOS and Android applications utilizing Flutter, React Native, Dart, and REST APIs at Zomato Bangalore Engineering Hub.", "Mobile App Development, Flutter, React Native, Dart, Swift, Kotlin, Java, REST API", "internal", None),
            ("QA Automation Engineer", "Cognizant", "Hyderabad, India", "Automate regression testing, end-to-end API test suites, and continuous testing workflows using PyTest and Selenium at Cognizant Hyderabad.", "QA Testing, Automation Testing, PyTest, Selenium, Python, Java, API Testing, Unit Testing", "internal", None),
            ("Systems Software Engineer", "Intel India", "Bangalore, India", "Write high-performance low-level systems software with C, C++, Rust, and multi-threaded Linux OS programming at Intel Bangalore Campus.", "C, C++, Rust, Linux, Operating Systems, Multithreading, Memory Management, Algorithms", "internal", None),
            ("Robotics and AI Engineer", "TCS Research", "Hyderabad, India", "Build robotic perception and control pipelines with ROS, C++, Python, Computer Vision, and AI algorithms at TCS Research Labs Hyderabad.", "Robotics, ROS, Artificial Intelligence, C++, Python, Computer Vision, Control Systems", "internal", None)
        ]
        cursor.executemany(
            """INSERT INTO job_listings
               (title, company, location, description, required_skills, application_type, application_url, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
            seed_jobs
        )
        conn.commit()

    conn.close()
