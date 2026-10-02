import re

# Standard English Stopwords list
STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t', 'as', 
    'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'can\'t', 
    'cannot', 'could', 'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during', 
    'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 
    'he\'d', 'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 
    'i', 'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 
    'let\'s', 'me', 'more', 'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 
    'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d', 
    'she\'ll', 'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their', 
    'theirs', 'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re', 
    'they\'ve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 
    'we\'d', 'we\'ll', 'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where', 
    'where\'s', 'which', 'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t', 
    'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves'
}

def clean_text(text):
    """
    Cleans raw text by removing URLs, emails, special characters, 
    lowercasing, and normalizing spaces.
    """
    if not text:
        return ""
        
    text = text.lower()
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    # Remove Emails
    text = re.sub(r'\S+@\S+', ' ', text)
    # Replace non-alphanumeric except +, #, ., - (crucial for C++, C#, .NET, Node.js)
    text = re.sub(r'[^a-z0-9\+#\.\-\s]', ' ', text)
    # Remove standalone dots or hyphens
    text = re.sub(r'\s+[\.-]+\s+', ' ', text)
    # Replace multiple whitespaces with single space
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text):
    """
    Tokenizes text into words.
    """
    cleaned = clean_text(text)
    return cleaned.split()

def remove_stopwords(tokens):
    """
    Filters out English stopwords from a token list.
    """
    return [token for token in tokens if token not in STOP_WORDS]

def preprocess_text(text):
    """
    Full text preprocessing pipeline: clean -> tokenize -> remove stopwords -> rejoin.
    """
    tokens = tokenize(text)
    filtered = remove_stopwords(tokens)
    return " ".join(filtered)
