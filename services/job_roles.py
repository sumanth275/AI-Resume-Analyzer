JOB_ROLES = {

    "Python Developer": {
        "description": """
        Python Developer with strong knowledge of Python, Flask, Django,
        FastAPI, SQL, Git, REST API, HTML, CSS, JavaScript, databases,
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
        NLP, Computer Vision, SQL, Git and Data Science.
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
    },

    "AI Engineer": {
        "description": """
        AI Engineer with knowledge of Python, Artificial Intelligence,
        Machine Learning, Deep Learning, TensorFlow, PyTorch,
        Scikit-learn, NLP, Computer Vision, SQL and Git.
        """
    },

    "Deep Learning Engineer": {
        "description": """
        Deep Learning Engineer with knowledge of Python, Deep Learning,
        TensorFlow, PyTorch, Neural Networks, Machine Learning,
        NumPy, Pandas, Computer Vision, NLP and Mathematics.
        """
    },

    "NLP Engineer": {
        "description": """
        NLP Engineer with knowledge of Python, Natural Language Processing,
        Machine Learning, Deep Learning, NLP, Transformers, Text Processing,
        TensorFlow, PyTorch, Scikit-learn and Data Science.
        """
    },

    "Computer Vision Engineer": {
        "description": """
        Computer Vision Engineer with knowledge of Python, Computer Vision,
        OpenCV, Deep Learning, Machine Learning, TensorFlow, PyTorch,
        Image Processing, Neural Networks and NumPy.
        """
    },

    "Generative AI Engineer": {
        "description": """
        Generative AI Engineer with knowledge of Python, Generative AI,
        Artificial Intelligence, Machine Learning, Deep Learning,
        Natural Language Processing, Large Language Models,
        Transformers, APIs, Git and databases.
        """
    },

    "AI/ML Researcher": {
        "description": """
        AI and Machine Learning Researcher with knowledge of Python,
        Artificial Intelligence, Machine Learning, Deep Learning,
        Statistics, Mathematics, NLP, Computer Vision,
        Scikit-learn, TensorFlow, PyTorch and Data Science.
        """
    },

    "MLOps Engineer": {
        "description": """
        MLOps Engineer with knowledge of Python, Machine Learning,
        Docker, Kubernetes, Git, CI/CD, AWS, Azure, GCP,
        TensorFlow, PyTorch, SQL and model deployment.
        """
    },

    "Data Engineer": {
        "description": """
        Data Engineer with knowledge of Python, SQL, databases,
        ETL, data pipelines, Apache Spark, Hadoop, Kafka,
        Pandas, NumPy, cloud computing and data warehousing.
        """
    },

    "Business Intelligence Analyst": {
        "description": """
        Business Intelligence Analyst with knowledge of SQL, Excel,
        Power BI, Tableau, Data Visualization, Statistics,
        Data Analysis, databases and reporting.
        """
    },

    "Big Data Engineer": {
        "description": """
        Big Data Engineer with knowledge of Python, SQL, Hadoop,
        Apache Spark, Kafka, Big Data, data pipelines, databases,
        cloud computing and distributed systems.
        """
    },

    "Software Engineer": {
        "description": """
        Software Engineer with knowledge of Python, Java, C,
        Data Structures, Algorithms, Object-Oriented Programming,
        SQL, Git, databases, software development and REST API.
        """
    },

    "Backend Developer": {
        "description": """
        Backend Developer with knowledge of Python, Flask, Django,
        FastAPI, Node.js, Express.js, REST API, SQL, databases,
        Git, authentication and server-side development.
        """
    },

    "Full Stack Developer": {
        "description": """
        Full Stack Developer with knowledge of HTML, CSS, JavaScript,
        React, Node.js, Express.js, Python, Flask, SQL, databases,
        REST API, Git and responsive web development.
        """
    },

    "AI Product Engineer": {
        "description": """
        AI Product Engineer with knowledge of Python, Artificial Intelligence,
        Machine Learning, Generative AI, APIs, databases, software development,
        Git, REST API, product development and data analysis.
        """
    },

    "Robotics and AI Engineer": {
        "description": """
        Robotics and AI Engineer with knowledge of Python, Artificial Intelligence,
        Machine Learning, Computer Vision, Robotics, Deep Learning,
        OpenCV, ROS, sensors, automation and embedded systems.
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