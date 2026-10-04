JOB_ROLES = {
    "Python Developer": {
        "description": """
        Python developer with knowledge of Python, Flask, Django, FastAPI,
        SQL, Git, REST API, HTML, CSS, JavaScript, databases,
        object-oriented programming, data structures and algorithms.
        """
    },

    "Data Analyst": {
        "description": """
        Data Analyst with knowledge of Python, SQL, Excel, Pandas, NumPy,
        data analysis, data analytics, data visualization, statistics,
        Tableau, Power BI and databases.
        """
    },

    "Machine Learning Engineer": {
        "description": """
        Machine Learning Engineer with knowledge of Python, Machine Learning,
        Deep Learning, Scikit-learn, TensorFlow, PyTorch, NumPy, Pandas,
        NLP, Computer Vision, SQL, Git and data science.
        """
    },

    "Data Scientist": {
        "description": """
        Data Scientist with knowledge of Python, Machine Learning,
        Deep Learning, Statistics, Data Science, Pandas, NumPy,
        Scikit-learn, TensorFlow, SQL, Data Visualization,
        NLP and Data Analytics.
        """
    },

    "Web Developer": {
        "description": """
        Web Developer with knowledge of HTML, CSS, JavaScript, React,
        Angular, Node.js, Express.js, Flask, REST API, SQL, Git
        and responsive web development.
        """
    }
}


def get_job_roles():
    """Return all available predefined job roles."""
    return JOB_ROLES


def get_job_description(role_name):
    """Return the job description for a selected role."""
    role = JOB_ROLES.get(role_name)
    if role:
        return role["description"].strip()
    return ""