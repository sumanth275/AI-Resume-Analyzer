import re

# Comprehensive Master Skill Taxonomy
SKILL_TAXONOMY = {
    # Programming Languages
    'python', 'java', 'c++', 'c#', 'c', 'javascript', 'typescript', 'golang', 'go', 'rust', 
    'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'html', 'html5', 'css', 'css3', 
    'sql', 'pl/sql', 'bash', 'shell', 'powershell', 'dart', 'assembly', 'perl',

    # Web & Frontend Technologies
    'react', 'react.js', 'reactjs', 'angular', 'angularjs', 'vue', 'vue.js', 'vuejs', 
    'next.js', 'nextjs', 'nuxt.js', 'node.js', 'nodejs', 'express', 'express.js', 
    'bootstrap', 'tailwind', 'tailwindcss', 'jquery', 'sass', 'less', 'webpack', 
    'vite', 'redox', 'redux', 'material ui', 'mui',

    # Backend & Frameworks
    'flask', 'django', 'fastapi', 'spring', 'spring boot', 'asp.net', '.net', '.net core', 
    'laravel', 'symfony', 'rails', 'ruby on rails', 'graphql', 'rest api', 'restful api', 
    'grpc', 'microservices', 'websockets',

    # Databases & Storage
    'sqlite', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'oracle', 
    'sql server', 'mssql', 'cassandra', 'elasticsearch', 'dynamodb', 'mariadb', 
    'couchdb', 'neo4j', 'firebase', 'supabase',

    # Cloud & Infrastructure
    'aws', 'amazon web services', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 
    'k8s', 'terraform', 'ansible', 'jenkins', 'git', 'github', 'gitlab', 'bitbucket', 
    'ci/cd', 'nginx', 'apache', 'linux', 'unix', 'ubuntu', 'serverless', 'cloudformation',

    # Data Science, ML & AI
    'machine learning', 'deep learning', 'nlp', 'natural language processing', 
    'computer vision', 'data science', 'data analysis', 'data analytics', 'data visualization', 
    'pandas', 'numpy', 'scikit-learn', 'sklearn', 'tensorflow', 'pytorch', 'keras', 
    'opencv', 'scipy', 'matplotlib', 'seaborn', 'spark', 'pyspark', 'hadoop', 'tableau', 
    'power bi', 'bigquery', 'snowflake', 'llm', 'generative ai',

    # Software Engineering & Practices
    'object-oriented programming', 'oop', 'data structures', 'algorithms', 'system design', 
    'agile', 'scrum', 'kanban', 'tdd', 'test-driven development', 'unit testing', 'integration testing', 
    'version control', 'code review', 'debugging', 'refactoring',

    # Concepts & Soft Skills
    'leadership', 'communication', 'problem solving', 'teamwork', 'project management', 
    'critical thinking', 'time management', 'analytical skills', 'collaboration'
}

# Alias mapping to canonical skill names
SKILL_ALIASES = {
    'reactjs': 'React',
    'react.js': 'React',
    'react': 'React',
    'vuejs': 'Vue.js',
    'vue.js': 'Vue.js',
    'vue': 'Vue.js',
    'angularjs': 'Angular',
    'angular': 'Angular',
    'nodejs': 'Node.js',
    'node.js': 'Node.js',
    'node': 'Node.js',
    'express.js': 'Express.js',
    'express': 'Express.js',
    'nextjs': 'Next.js',
    'next.js': 'Next.js',
    'python': 'Python',
    'java': 'Java',
    'c++': 'C++',
    'c#': 'C#',
    'c': 'C',
    'javascript': 'JavaScript',
    'typescript': 'TypeScript',
    'golang': 'Go',
    'go': 'Go',
    'rust': 'Rust',
    'ruby': 'Ruby',
    'php': 'PHP',
    'html': 'HTML',
    'html5': 'HTML5',
    'css': 'CSS',
    'css3': 'CSS3',
    'sql': 'SQL',
    'flask': 'Flask',
    'django': 'Django',
    'fastapi': 'FastAPI',
    'spring boot': 'Spring Boot',
    'spring': 'Spring',
    'asp.net': 'ASP.NET',
    '.net': '.NET',
    'docker': 'Docker',
    'kubernetes': 'Kubernetes',
    'k8s': 'Kubernetes',
    'aws': 'AWS',
    'azure': 'Azure',
    'gcp': 'GCP',
    'git': 'Git',
    'github': 'GitHub',
    'gitlab': 'GitLab',
    'jenkins': 'Jenkins',
    'terraform': 'Terraform',
    'ansible': 'Ansible',
    'sqlite': 'SQLite',
    'mysql': 'MySQL',
    'postgresql': 'PostgreSQL',
    'postgres': 'PostgreSQL',
    'mongodb': 'MongoDB',
    'redis': 'Redis',
    'oracle': 'Oracle',
    'elasticsearch': 'Elasticsearch',
    'machine learning': 'Machine Learning',
    'deep learning': 'Deep Learning',
    'nlp': 'NLP',
    'natural language processing': 'NLP',
    'data science': 'Data Science',
    'pandas': 'Pandas',
    'numpy': 'NumPy',
    'scikit-learn': 'Scikit-learn',
    'sklearn': 'Scikit-learn',
    'tensorflow': 'TensorFlow',
    'pytorch': 'PyTorch',
    'keras': 'Keras',
    'opencv': 'OpenCV',
    'rest api': 'REST API',
    'restful api': 'REST API',
    'graphql': 'GraphQL',
    'microservices': 'Microservices',
    'agile': 'Agile',
    'scrum': 'Scrum',
    'linux': 'Linux',
    'ci/cd': 'CI/CD'
}

def extract_skills(text):
    """
    Extracts recognized technical and soft skills from raw or cleaned text.
    Uses regex boundaries to prevent false positives (e.g. 'c' matching 'cloud').
    """
    if not text:
        return []

    text_lower = text.lower()
    found_skills = set()

    # Pre-sort skills by length descending so longer matching phrases match first (e.g., 'spring boot' before 'spring')
    sorted_skills = sorted(SKILL_TAXONOMY, key=len, reverse=True)

    for skill in sorted_skills:
        # Construct boundary pattern appropriate for special characters like C++, C#, .NET
        if skill in ['c++', 'c#', '.net', '.net core', 'c', 'r', 'go']:
            # Handle special symbols
            escaped = re.escape(skill)
            pattern = rf'(?:^|[\s,;:\(\)\[\]/]){escaped}(?:[\s,;:\(\)\[\]/.]|$)'
        else:
            escaped = re.escape(skill)
            pattern = rf'\b{escaped}\b'

        if re.search(pattern, text_lower):
            # Normalize to canonical format if available, otherwise title case
            canonical = SKILL_ALIASES.get(skill, skill.title())
            found_skills.add(canonical)

    return sorted(list(found_skills))
