import re
from typing import List, Optional, Tuple
from app.schemas.analysis import CandidateProfile
from app.services.model_loader import get_spacy_nlp

COMMON_JOB_TITLES = [
    "software engineer", "senior software engineer", "full stack developer", "full stack engineer",
    "frontend developer", "frontend engineer", "backend developer", "backend engineer",
    "data scientist", "machine learning engineer", "data engineer", "ai engineer",
    "devops engineer", "cloud architect", "site reliability engineer", "sre",
    "product manager", "project manager", "technical lead", "tech lead",
    "engineering manager", "systems architect", "solutions architect", "database administrator",
    "qa engineer", "quality assurance engineer", "mobile developer", "ios developer", "android developer",
    "security engineer", "cybersecurity analyst", "ui/ux designer", "scrum master"
]

DEGREE_PATTERNS = [
    r"\b(?:bachelor(?:'s)?|b\.?s\.?|b\.?a\.?|b\.?tech\.?|b\.?e\.?)\b(?:\s+(?:of|in)\s+[a-zA-Z\s]+)?",
    r"\b(?:master(?:'s)?|m\.?s\.?|m\.?a\.?|m\.?tech\.?|m\.?b\.?a\.?)\b(?:\s+(?:of|in)\s+[a-zA-Z\s]+)?",
    r"\b(?:ph\.?d\.?|doctorate|doctoral)\b(?:\s+(?:of|in)\s+[a-zA-Z\s]+)?",
    r"\b(?:associate(?:'s)?\s+degree|diploma)\b(?:\s+(?:of|in)\s+[a-zA-Z\s]+)?"
]


def extract_candidate_name(text: str) -> Optional[str]:
    """Extract candidate name using top lines heuristics and spaCy NER."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return None

    # Common non-name words in resume headers
    skip_words = {
        "resume", "curriculum", "vitae", "cv", "page", "profile", "contact",
        "email", "phone", "address", "summary", "experience", "education",
        "skills", "projects", "objective", "portfolio", "github", "linkedin"
    }

    # Check top 5 lines
    candidate_lines = lines[:5]
    for line in candidate_lines:
        # Ignore lines with email or URL
        if "@" in line or "http" in line or ".com" in line or "www." in line:
            continue
        clean_line = re.sub(r"[^a-zA-Z\s\.\-]", "", line).strip()
        words = clean_line.split()
        if 2 <= len(words) <= 4:
            # Check if words are capitalized and not typical header words
            if all(w.lower() not in skip_words for w in words):
                if any(w[0].isupper() for w in words if w):
                    return clean_line

    # Fallback to spaCy NER
    try:
        nlp = get_spacy_nlp()
        doc = nlp("\n".join(candidate_lines))
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                clean_ent = ent.text.strip()
                words = clean_ent.split()
                if 2 <= len(words) <= 4 and all(w.lower() not in skip_words for w in words):
                    return clean_ent
    except Exception:
        pass

    return None


def extract_contact_info(text: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Extract email, phone, linkedin, github, and portfolio links."""
    # Email
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
    email = email_match.group(0) if email_match else None

    # Phone
    phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    phone_match = re.search(phone_pattern, text)
    phone = phone_match.group(0) if phone_match else None

    # LinkedIn
    linkedin_match = re.search(r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+", text, re.IGNORECASE)
    linkedin = linkedin_match.group(0) if linkedin_match else None

    # GitHub
    github_match = re.search(r"(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+", text, re.IGNORECASE)
    github = github_match.group(0) if github_match else None

    # Portfolio
    portfolio = None
    url_matches = re.findall(r"https?:\/\/(?!www\.linkedin|www\.github)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?", text, re.IGNORECASE)
    if url_matches:
        portfolio = url_matches[0]

    return email, phone, linkedin, github, portfolio


def extract_job_titles(text: str) -> List[str]:
    """Extract detected professional job titles from the resume text."""
    lower_text = text.lower()
    detected = []
    for title in COMMON_JOB_TITLES:
        # Match word boundaries
        pattern = r"\b" + re.escape(title) + r"\b"
        if re.search(pattern, lower_text):
            detected.append(title.title())
    return detected


def extract_education(text: str) -> List[str]:
    """Detect educational degree indicators and academic qualifications."""
    found_degrees = set()
    for pattern in DEGREE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            clean = re.sub(r"\s+", " ", m).strip().title()
            if len(clean) > 2:
                found_degrees.add(clean)
    return sorted(list(found_degrees))


def extract_experience_info(text: str) -> Tuple[List[str], Optional[float]]:
    """Extract experience indicators and estimate total experience in years."""
    indicators: List[str] = []

    # Look for explicit statements like "5+ years of experience" or "over 7 years"
    exp_regex = r"(\d{1,2}(?:\.\d+)?)\+?\s*(?:-\s*\d{1,2})?\s*years?(?:\s+of)?(?:\s+(?:professional|industry|relevant))?\s*experience"
    exp_matches = re.finditer(exp_regex, text, re.IGNORECASE)
    explicit_years: List[float] = []
    for m in exp_matches:
        indicators.append(m.group(0).strip())
        try:
            explicit_years.append(float(m.group(1)))
        except ValueError:
            pass

    # Look for year ranges like "2018 - 2023" or "2020 to Present"
    date_range_regex = r"\b(19\d{2}|20\d{2})\s*(?:-|–|—|to)\s*(19\d{2}|20\d{2}|present|current)\b"
    range_matches = re.finditer(date_range_regex, text, re.IGNORECASE)
    total_range_years = 0.0
    current_year = 2026

    for rm in range_matches:
        start_year = int(rm.group(1))
        end_str = rm.group(2).lower()
        end_year = current_year if ("present" in end_str or "current" in end_str) else int(end_str)
        if 1980 <= start_year <= current_year and end_year >= start_year:
            diff = min(end_year - start_year, 15)
            total_range_years += diff
            indicators.append(f"{start_year} - {rm.group(2).capitalize()}")

    # Determine estimated total years
    estimated_years: Optional[float] = None
    if explicit_years:
        estimated_years = max(explicit_years)
    elif total_range_years > 0:
        # Cap at 30 years to avoid overlapping date anomalies
        estimated_years = min(round(total_range_years, 1), 30.0)

    # Deduplicate indicators preserving order
    seen = set()
    unique_indicators = [x for x in indicators if not (x in seen or seen.add(x))]
    return unique_indicators, estimated_years


def extract_candidate_profile(text: str) -> CandidateProfile:
    """Consolidated candidate profile extraction."""
    name = extract_candidate_name(text)
    email, phone, linkedin, github, portfolio = extract_contact_info(text)
    detected_titles = extract_job_titles(text)
    education = extract_education(text)
    exp_indicators, total_exp = extract_experience_info(text)

    return CandidateProfile(
        name=name,
        email=email,
        phone=phone,
        linkedin=linkedin,
        github=github,
        portfolio=portfolio,
        detected_titles=detected_titles,
        education=education,
        experience_indicators=exp_indicators,
        total_experience_years=total_exp
    )
