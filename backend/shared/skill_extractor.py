"""Keyword-based skill extraction and matching utilities."""

import re
from typing import Any, Dict, List, Set

# SKILLS_DATABASE: mapping category names to lists of canonical skill keywords
SKILLS_DATABASE: Dict[str, List[str]] = {
    "programming_languages": [
        "python",
        "javascript",
        "typescript",
        "java",
        "c++",
        "c#",
        "golang",
        "rust",
        "ruby",
        "php",
        "swift",
        "kotlin",
        "scala",
        "r",
        "sql",
    ],
    "web_frameworks": [
        "react",
        "angular",
        "vue",
        "next.js",
        "node.js",
        "express",
        "django",
        "flask",
        "fastapi",
        "spring boot",
        "asp.net",
        "laravel",
        "ruby on rails",
    ],
    "databases": [
        "postgresql",
        "mysql",
        "mongodb",
        "dynamodb",
        "redis",
        "elasticsearch",
        "cassandra",
        "sqlite",
        "oracle",
        "microsoft sql server",
        "neo4j",
    ],
    "cloud_services": [
        "amazon web services",
        "microsoft azure",
        "google cloud platform",
        "aws lambda",
        "aws s3",
        "aws dynamodb",
        "aws sqs",
        "aws textract",
        "amazon ec2",
        "cloudformation",
        "terraform",
    ],
    "devops_tools": [
        "docker",
        "kubernetes",
        "jenkins",
        "git",
        "github actions",
        "gitlab ci",
        "ansible",
        "helm",
        "prometheus",
        "grafana",
        "nginx",
    ],
    "data_science": [
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "tensorflow",
        "pytorch",
        "pandas",
        "numpy",
        "scikit-learn",
        "nlp",
        "computer vision",
        "data analysis",
    ],
    "soft_skills": [
        "communication",
        "leadership",
        "teamwork",
        "problem solving",
        "time management",
        "critical thinking",
        "collaboration",
        "adaptability",
        "agile",
        "scrum",
    ],
    "other_tools": [
        "rest api",
        "graphql",
        "grpc",
        "microservices",
        "linux",
        "jira",
        "postman",
        "vite",
        "webpack",
        "tailwind css",
    ],
}

# ALIASES: map variations/synonyms/abbreviations to canonical skill names
ALIASES: Dict[str, str] = {
    # Programming languages & variations
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "cpp": "c++",
    "cplusplus": "c++",
    "csharp": "c#",
    "go": "golang",
    "rb": "ruby",
    # Frameworks
    "react.js": "react",
    "reactjs": "react",
    "vue.js": "vue",
    "vuejs": "vue",
    "angularjs": "angular",
    "nextjs": "next.js",
    "nodejs": "node.js",
    "expressjs": "express",
    "spring": "spring boot",
    "springboot": "spring boot",
    "dotnet": "asp.net",
    ".net": "asp.net",
    "rails": "ruby on rails",
    # Cloud & DevOps
    "aws": "amazon web services",
    "azure": "microsoft azure",
    "gcp": "google cloud platform",
    "google cloud": "google cloud platform",
    "k8s": "kubernetes",
    "ec2": "amazon ec2",
    "s3": "aws s3",
    "lambda": "aws lambda",
    "sqs": "aws sqs",
    "textract": "aws textract",
    # Databases
    "postgres": "postgresql",
    "mongo": "mongodb",
    "elastic search": "elasticsearch",
    "mssql": "microsoft sql server",
    "sql server": "microsoft sql server",
    # Data Science
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "sklearn": "scikit-learn",
    "natural language processing": "nlp",
    # Other tools
    "rest": "rest api",
    "restful api": "rest api",
    "restful apis": "rest api",
    "rest apis": "rest api",
    "tailwind": "tailwind css",
    "tailwindcss": "tailwind css",
}


def normalize_text(text: str) -> str:
    """Lowercase, remove special characters (preserving essential skill symbols), and normalize whitespace.

    Args:
        text: Raw input string.

    Returns:
        Normalized string with uniform whitespace and lowercase text.
    """
    if not text:
        return ""
    lowered = text.lower()
    # Retain characters often found in skills like c++, c#, .net, next.js, node.js
    cleaned = re.sub(r"[^a-z0-9+#.\s-]", " ", lowered)
    normalized = re.sub(r"\s+", " ", cleaned).strip()
    return normalized


def _build_search_list() -> List[tuple[str, str]]:
    """Build a list of tuples (token_or_phrase, canonical_name) sorted by length descending."""
    candidates = {}
    for canonical in ALIASES.values():
        candidates[canonical] = canonical
    for category_skills in SKILLS_DATABASE.values():
        for skill in category_skills:
            candidates[skill] = skill
    for alias, canonical in ALIASES.items():
        candidates[alias] = canonical

    # Sort descending by token length so multi-word phrases match before substrings
    items = sorted(candidates.items(), key=lambda x: len(x[0]), reverse=True)
    return items


SEARCH_ITEMS = _build_search_list()


def extract_skills(text: str) -> List[str]:
    """Extract recognized skills from text by matching against SKILLS_DATABASE and ALIASES.

    Handles multi-word skills and aliases.

    Args:
        text: Resume or profile text.

    Returns:
        List of distinct canonical skill names detected in text.
    """
    if not text:
        return []

    norm = normalize_text(text)
    matched_skills: Set[str] = set()

    # Search for each phrase or token with word/boundary constraints
    for phrase, canonical in SEARCH_ITEMS:
        # Build regex for word-like boundary
        # If phrase contains punctuation like c++, c#, .net, escape it
        escaped = re.escape(phrase)
        # We need boundaries that treat whitespace or string ends as boundaries
        pattern = rf"(?:^|[\s,;/()]){escaped}(?:$|[\s,;/()])"
        if re.search(pattern, norm):
            matched_skills.add(canonical)

    return sorted(list(matched_skills))


def extract_requirements(requirements_text: str) -> List[str]:
    """Extract skill requirements from job description text.

    Args:
        requirements_text: Job description or requirements text.

    Returns:
        List of distinct canonical skill names.
    """
    return extract_skills(requirements_text)


def match_skills(resume_text: str, requirements_text: str) -> Dict[str, Any]:
    """Compare resume skills against job requirements.

    Args:
        resume_text: Extracted text from candidate resume.
        requirements_text: Raw requirements text from job description.

    Returns:
        Dictionary containing:
            - match_percentage: float (0.0 to 100.0)
            - matched_skills: list of matched skills
            - missing_skills: list of missing skills
            - resume_skills: list of all skills found in resume
            - required_skills: list of all skills found in requirements
    """
    resume_skills_set = set(extract_skills(resume_text))
    required_skills_set = set(extract_requirements(requirements_text))

    matched_set = resume_skills_set.intersection(required_skills_set)
    missing_set = required_skills_set.difference(resume_skills_set)

    if required_skills_set:
        match_percentage = round((len(matched_set) / len(required_skills_set)) * 100.0, 2)
    else:
        match_percentage = 0.0

    return {
        "match_percentage": match_percentage,
        "matched_skills": sorted(list(matched_set)),
        "missing_skills": sorted(list(missing_set)),
        "resume_skills": sorted(list(resume_skills_set)),
        "required_skills": sorted(list(required_skills_set)),
    }
