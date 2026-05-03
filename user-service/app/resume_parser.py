import io
from pypdf import PdfReader
import re

# A massive dictionary of tech skills for basic keyword matching
TECH_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "go", "rust", "swift", "kotlin",
    "sql", "nosql", "mongodb", "postgresql", "mysql", "redis", "cassandra", "elasticsearch",
    "react", "angular", "vue", "svelte", "next.js", "node.js", "express", "django", "flask", "fastapi", "spring",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible", "jenkins", "ci/cd", "github actions",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "scikit-learn", "pandas",
    "numpy", "data science", "data engineering", "spark", "hadoop", "kafka", "rabbitmq", "graphql", "rest api",
    "html", "css", "tailwind", "sass", "bootstrap", "linux", "bash", "git", "agile", "scrum"
}

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Read raw bytes of a PDF and extract all text."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "
        return text
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

def extract_skills_from_text(text: str) -> list[str]:
    """Match words in the text against the known TECH_SKILLS dictionary."""
    # Convert text to lowercase and split into words/tokens
    # We use a regex to capture words or multi-word phrases (simplistic approach)
    text_lower = text.lower()
    
    found_skills = set()
    for skill in TECH_SKILLS:
        # Create a boundary regex for the skill
        # e.g. for "c++" we need to be careful with word boundaries
        escaped_skill = re.escape(skill)
        pattern = r'\b' + escaped_skill + r'(?!\w)'
        # Special case for C++, C#
        if skill in ("c++", "c#"):
            pattern = r'\b' + escaped_skill
            
        if re.search(pattern, text_lower):
            found_skills.add(skill)
            
    return list(found_skills)
