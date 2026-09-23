import re
from typing import List, Dict, Tuple, Optional
from app.schemas.analysis import (
    ScoreBreakdown,
    ScoreComponent,
    MatchedSkill,
    MissingSkill,
    ImprovementSuggestion,
    CandidateProfile
)


def calculate_title_and_experience_alignment(
    profile: CandidateProfile,
    jd_text: str
) -> Tuple[float, str]:
    """Calculate job title and experience level alignment (0-100)."""
    score = 0.0
    reasons = []

    lower_jd = jd_text.lower()

    # 1. Job Title Alignment (Up to 60 points)
    candidate_titles_lower = [t.lower() for t in profile.detected_titles]
    target_role_words = set()

    # Identify target role words from the first 500 characters of JD
    jd_intro = lower_jd[:600]
    core_roles = [
        "software engineer", "frontend", "backend", "full stack", "data scientist",
        "machine learning", "devops", "cloud", "product manager", "qa engineer",
        "architect", "engineering manager", "lead", "developer"
    ]

    matched_roles = [r for r in core_roles if r in jd_intro]
    matched_target = False

    for title in candidate_titles_lower:
        for role in matched_roles:
            if role in title:
                matched_target = True
                break

    if matched_target:
        score += 60.0
        reasons.append("Detected resume job title closely matches target role.")
    elif candidate_titles_lower:
        # Partial alignment (candidate has technical title)
        score += 35.0
        reasons.append("Resume contains relevant professional titles.")
    else:
        score += 15.0
        reasons.append("Target role titles were not clearly identifiable in resume headline.")

    # 2. Seniority & Experience Alignment (Up to 40 points)
    jd_years_match = re.search(r"(\d{1,2})\+?\s*(?:years?|yrs)", lower_jd)
    required_years = float(jd_years_match.group(1)) if jd_years_match else 2.0

    candidate_years = profile.total_experience_years

    if candidate_years is not None:
        if candidate_years >= required_years:
            score += 40.0
            reasons.append(f"Experience (~{candidate_years} yrs) meets or exceeds job requirements (~{required_years} yrs).")
        elif candidate_years >= required_years * 0.6:
            score += 25.0
            reasons.append(f"Experience (~{candidate_years} yrs) is moderately aligned with requirement (~{required_years} yrs).")
        else:
            score += 15.0
            reasons.append(f"Detected experience (~{candidate_years} yrs) is below stated expectation (~{required_years} yrs).")
    else:
        # If dates are detected but total couldn't be summed
        if profile.experience_indicators:
            score += 25.0
            reasons.append("Experience date ranges detected but total duration is indeterminate.")
        else:
            score += 10.0
            reasons.append("Could not extract explicit years of experience.")

    final_score = min(max(round(score, 1), 0.0), 100.0)
    explanation = " ".join(reasons)
    return final_score, explanation


def calculate_resume_completeness(
    profile: CandidateProfile,
    warnings: List[str],
    text_length: int
) -> Tuple[float, str]:
    """Evaluate structural completeness, contactability, and parseability (0-100)."""
    score = 0.0
    items = []

    # Email (20 pts)
    if profile.email:
        score += 20.0
        items.append("Email detected")
    else:
        items.append("Email missing")

    # Phone (20 pts)
    if profile.phone:
        score += 20.0
        items.append("Phone detected")
    else:
        items.append("Phone missing")

    # Professional profiles (15 pts)
    if profile.linkedin or profile.github or profile.portfolio:
        score += 15.0
        items.append("Professional profile link (LinkedIn/GitHub/Portfolio) included")

    # Education (15 pts)
    if profile.education:
        score += 15.0
        items.append("Education section detected")

    # Experience indicators (15 pts)
    if profile.experience_indicators or profile.detected_titles:
        score += 15.0
        items.append("Work history / job titles detected")

    # Parse quality & formatting (15 pts)
    if not warnings and text_length > 300:
        score += 15.0
        items.append("Clean text extraction without warnings")
    else:
        score += 5.0
        items.append("Minor parsing or text density warnings")

    final_score = min(max(round(score, 1), 0.0), 100.0)
    explanation = "; ".join(items) + "."
    return final_score, explanation


def generate_prioritized_suggestions(
    missing_required: List[MissingSkill],
    missing_preferred: List[MissingSkill],
    semantic_score: float,
    alignment_score: float,
    completeness_score: float,
    profile: CandidateProfile
) -> List[ImprovementSuggestion]:
    """Generate 3-6 actionable, prioritized improvement recommendations."""
    suggestions: List[ImprovementSuggestion] = []

    # Suggestion 1: Missing Required Skills (High Priority)
    if missing_required:
        top_missing_req = [s.name for s in missing_required[:4]]
        suggestions.append(ImprovementSuggestion(
            priority="High",
            title=f"Add Core Required Skills: {', '.join(top_missing_req)}",
            action=f"If you have hands-on experience with {', '.join(top_missing_req)}, explicitly feature them under your Skills section and detail practical usage in recent project bullet points.",
            context="The job description explicitly prioritizes these competencies as mandatory qualifications."
        ))

    # Suggestion 2: Low Semantic Similarity / Terminology Gap (High or Medium Priority)
    if semantic_score < 60.0:
        suggestions.append(ImprovementSuggestion(
            priority="High",
            title="Strengthen Contextual & Keyword Alignment",
            action="Incorporate industry-standard terminology, problem-domain terms, and verbs directly reflecting the job posting's duties into your project descriptions.",
            context=f"Your semantic similarity score is currently {semantic_score:.1f}%. Rewording project accomplishments to directly address the employer's domain improves relevance."
        ))

    # Suggestion 3: Missing Preferred / Bonus Skills (Medium Priority)
    if missing_preferred:
        top_missing_pref = [s.name for s in missing_preferred[:3]]
        suggestions.append(ImprovementSuggestion(
            priority="Medium",
            title=f"Highlight Preferred Skills: {', '.join(top_missing_pref)}",
            action=f"Consider mentioning any familiarity, coursework, personal projects, or certifications involving {', '.join(top_missing_pref)}.",
            context="Preferred skills serve as tie-breakers when evaluating candidates with matching core requirements."
        ))

    # Suggestion 4: Job Title / Headline Optimization (Medium Priority)
    if alignment_score < 70.0 and profile.detected_titles:
        suggestions.append(ImprovementSuggestion(
            priority="Medium",
            title="Refine Resume Title & Professional Summary",
            action="Align your top professional headline or summary statement with the exact target title from the job description (e.g., 'Senior Full Stack Engineer').",
            context="Recruiters scan the first 1/3 of your resume in seconds to determine job-title alignment."
        ))

    # Suggestion 5: Completeness & Contact Links (Low/Medium Priority)
    if not profile.linkedin or not profile.github:
        suggestions.append(ImprovementSuggestion(
            priority="Low",
            title="Add Professional Links (LinkedIn & GitHub / Portfolio)",
            action="Include clickable links to your updated LinkedIn profile and GitHub repository or live portfolio to validate your technical contributions.",
            context="Verified project repositories and professional profiles significantly enhance credibility."
        ))

    # Suggestion 6: Quantifiable Metrics (Always beneficial if list is short)
    if len(suggestions) < 3:
        suggestions.append(ImprovementSuggestion(
            priority="Medium",
            title="Quantify Project Impact with Metrics",
            action="Use the 'Accomplished [X], measured by [Y], by doing [Z]' formula (e.g. 'Improved API response latency by 35% through Redis caching').",
            context="Action-oriented metrics provide verifiable proof of your technical competence."
        ))

    # Return top 3-6 suggestions
    return suggestions[:6]


def calculate_overall_match(
    resume_skills: Dict[str, Dict[str, any]],
    req_skills: Dict[str, Dict[str, any]],
    pref_skills: Dict[str, Dict[str, any]],
    semantic_similarity: float,
    profile: CandidateProfile,
    jd_text: str,
    warnings: List[str],
    resume_text_len: int
) -> Tuple[float, str, ScoreBreakdown, List[MatchedSkill], List[MissingSkill], List[MissingSkill], List[ImprovementSuggestion], str]:
    """Calculate the transparent 0-100 Resume Match Score with 5 weighted pillars.

    Weights:
      - 40% Required-skill coverage
      - 20% Preferred-skill coverage
      - 20% Semantic similarity
      - 10% Job-title and experience alignment
      - 10% Resume completeness and parseability
    """
    matched_skills: List[MatchedSkill] = []
    missing_required_skills: List[MissingSkill] = []
    missing_preferred_skills: List[MissingSkill] = []

    # 1. Required Skills Match
    matched_req_count = 0
    total_req_count = len(req_skills)

    for s_name, s_info in req_skills.items():
        if s_name in resume_skills:
            matched_req_count += 1
            matched_skills.append(MatchedSkill(
                name=s_name,
                category=s_info.get("category", "General"),
                matched_via=resume_skills[s_name].get("matched_via"),
                is_required=True
            ))
        else:
            missing_required_skills.append(MissingSkill(
                name=s_name,
                category=s_info.get("category", "General"),
                is_required=True
            ))

    if total_req_count > 0:
        req_raw = (matched_req_count / total_req_count) * 100.0
        req_exp = f"Matched {matched_req_count} of {total_req_count} required core skills ({req_raw:.1f}%)."
    else:
        req_raw = 100.0 if matched_skills else 75.0
        req_exp = "No explicit required skills segregated in JD; baseline coverage awarded."

    # 2. Preferred Skills Match
    matched_pref_count = 0
    total_pref_count = len(pref_skills)

    for s_name, s_info in pref_skills.items():
        if s_name in resume_skills:
            matched_pref_count += 1
            matched_skills.append(MatchedSkill(
                name=s_name,
                category=s_info.get("category", "General"),
                matched_via=resume_skills[s_name].get("matched_via"),
                is_required=False
            ))
        else:
            missing_preferred_skills.append(MissingSkill(
                name=s_name,
                category=s_info.get("category", "General"),
                is_required=False
            ))

    if total_pref_count > 0:
        pref_raw = (matched_pref_count / total_pref_count) * 100.0
        pref_exp = f"Matched {matched_pref_count} of {total_pref_count} preferred skills ({pref_raw:.1f}%)."
    else:
        # If no preferred skills listed in JD, candidate is awarded full credit for this component
        pref_raw = 100.0
        pref_exp = "No secondary or preferred qualifications specified in job description."

    # 3. Semantic Similarity (Sentence Transformers Cosine Similarity)
    # semantic_similarity is in [0.0, 1.0]
    sem_raw = min(max(semantic_similarity * 100.0, 0.0), 100.0)
    sem_exp = f"Cosine similarity between resume text and job description embeddings is {semantic_similarity:.2f} ({sem_raw:.1f}/100)."

    # 4. Job Title & Experience Alignment
    align_raw, align_exp = calculate_title_and_experience_alignment(profile, jd_text)

    # 5. Completeness & Parseability
    comp_raw, comp_exp = calculate_resume_completeness(profile, warnings, resume_text_len)

    # Weights
    w_req = 0.40
    w_pref = 0.20
    w_sem = 0.20
    w_align = 0.10
    w_comp = 0.10

    weighted_req = round(req_raw * w_req, 2)
    weighted_pref = round(pref_raw * w_pref, 2)
    weighted_sem = round(sem_raw * w_sem, 2)
    weighted_align = round(align_raw * w_align, 2)
    weighted_comp = round(comp_raw * w_comp, 2)

    total_score = weighted_req + weighted_pref + weighted_sem + weighted_align + weighted_comp
    overall_score = float(min(max(round(total_score, 1), 0.0), 100.0))

    # Determine qualitative match label
    if overall_score >= 80.0:
        score_label = "Strong Match"
    elif overall_score >= 65.0:
        score_label = "Good Match"
    elif overall_score >= 50.0:
        score_label = "Moderate Match"
    else:
        score_label = "Low Match"

    breakdown = ScoreBreakdown(
        required_skills=ScoreComponent(
            category="Required Skills Coverage",
            weight=w_req,
            raw_score=round(req_raw, 1),
            weighted_score=weighted_req,
            explanation=req_exp
        ),
        preferred_skills=ScoreComponent(
            category="Preferred Skills Coverage",
            weight=w_pref,
            raw_score=round(pref_raw, 1),
            weighted_score=weighted_pref,
            explanation=pref_exp
        ),
        semantic_similarity=ScoreComponent(
            category="Semantic Relevance",
            weight=w_sem,
            raw_score=round(sem_raw, 1),
            weighted_score=weighted_sem,
            explanation=sem_exp
        ),
        title_experience_alignment=ScoreComponent(
            category="Role & Experience Alignment",
            weight=w_align,
            raw_score=round(align_raw, 1),
            weighted_score=weighted_align,
            explanation=align_exp
        ),
        resume_completeness=ScoreComponent(
            category="Resume Completeness & Parseability",
            weight=w_comp,
            raw_score=round(comp_raw, 1),
            weighted_score=weighted_comp,
            explanation=comp_exp
        )
    )

    suggestions = generate_prioritized_suggestions(
        missing_required_skills,
        missing_preferred_skills,
        sem_raw,
        align_raw,
        comp_raw,
        profile
    )

    score_explanation = (
        f"Your transparent Resume Match Score is {overall_score:.1f}/100 ({score_label}). "
        f"It is derived from: 40% Required Skills ({weighted_req:.1f} pts), "
        f"20% Preferred Skills ({weighted_pref:.1f} pts), "
        f"20% Semantic Relevance ({weighted_sem:.1f} pts), "
        f"10% Role/Experience Alignment ({weighted_align:.1f} pts), and "
        f"10% Resume Completeness ({weighted_comp:.1f} pts). "
        "This metric represents an open, objective qualification match without proprietary ATS emulation."
    )

    return (
        overall_score,
        score_label,
        breakdown,
        matched_skills,
        missing_required_skills,
        missing_preferred_skills,
        suggestions,
        score_explanation
    )
