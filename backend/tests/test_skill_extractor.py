"""Unit tests for shared.skill_extractor module."""

import sys
import os

# Add backend root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shared.skill_extractor import (
    normalize_text,
    extract_skills,
    extract_requirements,
    match_skills,
    SKILLS_DATABASE,
    ALIASES,
)


class TestNormalizeText:
    """Tests for the normalize_text function."""

    def test_lowercases_text(self):
        assert normalize_text("Python JavaScript") == "python javascript"

    def test_removes_special_characters(self):
        result = normalize_text("Skills: Python, Java & SQL!")
        assert "python" in result
        assert "java" in result
        assert "sql" in result
        assert "&" not in result

    def test_preserves_skill_symbols(self):
        result = normalize_text("C++ and C# and .NET")
        assert "c++" in result
        assert "c#" in result
        assert ".net" in result

    def test_normalizes_whitespace(self):
        result = normalize_text("  python   javascript  ")
        assert result == "python javascript"

    def test_empty_string(self):
        assert normalize_text("") == ""

    def test_none_input(self):
        assert normalize_text(None) == ""


class TestExtractSkills:
    """Tests for the extract_skills function."""

    def test_extracts_single_skill(self):
        skills = extract_skills("I know Python very well")
        assert "python" in skills

    def test_extracts_multiple_skills(self):
        skills = extract_skills("Experienced in Python, JavaScript, and React development")
        assert "python" in skills
        assert "javascript" in skills
        assert "react" in skills

    def test_extracts_multiword_skills(self):
        skills = extract_skills("I have experience with machine learning and spring boot")
        assert "machine learning" in skills
        assert "spring boot" in skills

    def test_handles_aliases(self):
        skills = extract_skills("Proficient in JS and NodeJS and K8s")
        assert "javascript" in skills
        assert "node.js" in skills
        assert "kubernetes" in skills

    def test_case_insensitive(self):
        skills = extract_skills("PYTHON JAVASCRIPT REACT DOCKER")
        assert "python" in skills
        assert "javascript" in skills
        assert "react" in skills
        assert "docker" in skills

    def test_handles_dotted_skills(self):
        skills = extract_skills("Experience with Next.js and Node.js")
        assert "next.js" in skills
        assert "node.js" in skills

    def test_no_skills_found(self):
        skills = extract_skills("I like to eat pizza and watch movies")
        # Should return empty or minimal list
        assert isinstance(skills, list)

    def test_empty_input(self):
        assert extract_skills("") == []

    def test_none_input(self):
        assert extract_skills(None) == []

    def test_cloud_aliases(self):
        skills = extract_skills("Worked with AWS and GCP for cloud deployments")
        assert "amazon web services" in skills
        assert "google cloud platform" in skills


class TestExtractRequirements:
    """Tests for extract_requirements (delegates to extract_skills)."""

    def test_extracts_from_job_description(self):
        job_desc = """
        We are looking for a Full Stack Developer with:
        - Python and Django experience
        - React or Angular frontend skills
        - Docker and Kubernetes knowledge
        - PostgreSQL database experience
        """
        skills = extract_requirements(job_desc)
        assert "python" in skills
        assert "django" in skills
        assert "react" in skills
        assert "docker" in skills
        assert "kubernetes" in skills
        assert "postgresql" in skills


class TestMatchSkills:
    """Tests for the match_skills function."""

    def test_perfect_match(self):
        resume = "Expert in Python, Django, and PostgreSQL"
        requirements = "Need Python, Django, and PostgreSQL"
        result = match_skills(resume, requirements)

        assert result["match_percentage"] == 100.0
        assert len(result["missing_skills"]) == 0
        assert len(result["matched_skills"]) > 0

    def test_partial_match(self):
        resume = "I know Python and React"
        requirements = "Need Python, React, Docker, and Kubernetes"
        result = match_skills(resume, requirements)

        assert 0 < result["match_percentage"] < 100
        assert "python" in result["matched_skills"]
        assert "react" in result["matched_skills"]
        assert "docker" in result["missing_skills"]
        assert "kubernetes" in result["missing_skills"]

    def test_no_match(self):
        resume = "I know Python and Django"
        requirements = "Need Docker and Kubernetes"
        result = match_skills(resume, requirements)

        assert result["match_percentage"] == 0.0
        assert len(result["matched_skills"]) == 0
        assert len(result["missing_skills"]) > 0

    def test_empty_requirements(self):
        resume = "I know Python"
        requirements = ""
        result = match_skills(resume, requirements)

        assert result["match_percentage"] == 0.0
        assert result["matched_skills"] == []
        assert result["missing_skills"] == []

    def test_result_structure(self):
        result = match_skills("Python developer", "Need Python and Java")

        assert "match_percentage" in result
        assert "matched_skills" in result
        assert "missing_skills" in result
        assert "resume_skills" in result
        assert "required_skills" in result
        assert isinstance(result["match_percentage"], float)
        assert isinstance(result["matched_skills"], list)
        assert isinstance(result["missing_skills"], list)

    def test_alias_matching(self):
        """Resume uses alias 'JS', requirements say 'JavaScript' — should match."""
        resume = "Skilled in JS and NodeJS"
        requirements = "Need JavaScript and Node.js experience"
        result = match_skills(resume, requirements)

        assert "javascript" in result["matched_skills"]
        assert "node.js" in result["matched_skills"]
        assert result["match_percentage"] == 100.0

    def test_percentage_calculation(self):
        """With 2 out of 4 required skills, should get 50%."""
        resume = "Python and React developer"
        requirements = "Python, React, Docker, Kubernetes"
        result = match_skills(resume, requirements)

        assert result["match_percentage"] == 50.0
