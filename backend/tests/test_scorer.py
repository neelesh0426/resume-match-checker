from app.schemas.analysis import CandidateProfile
from app.services.scorer import calculate_overall_match, generate_prioritized_suggestions


def test_score_calculation_bounds_and_weights():
    resume_skills = {
        "Python": {"category": "Languages", "matched_via": None},
        "FastAPI": {"category": "Backend", "matched_via": None},
        "PostgreSQL": {"category": "Databases", "matched_via": "postgres"},
    }

    req_skills = {
        "Python": {"category": "Languages"},
        "FastAPI": {"category": "Backend"},
        "PostgreSQL": {"category": "Databases"},
        "Docker": {"category": "Cloud & DevOps"},  # Missing required
    }

    pref_skills = {
        "Redis": {"category": "Databases"},  # Missing preferred
    }

    profile = CandidateProfile(
        name="Test Candidate",
        email="test@example.com",
        phone="555-123-4567",
        linkedin="linkedin.com/in/test",
        github="github.com/test",
        detected_titles=["Backend Engineer"],
        education=["Bachelor of Science"],
        experience_indicators=["2020 - Present"],
        total_experience_years=4.0
    )

    (
        overall_score,
        score_label,
        breakdown,
        matched,
        missing_req,
        missing_pref,
        suggestions,
        explanation
    ) = calculate_overall_match(
        resume_skills=resume_skills,
        req_skills=req_skills,
        pref_skills=pref_skills,
        semantic_similarity=0.75,
        profile=profile,
        jd_text="Backend Engineer with Python and Docker",
        warnings=[],
        resume_text_len=1000
    )

    # Check bounds
    assert 0.0 <= overall_score <= 100.0
    assert score_label in ["Strong Match", "Good Match", "Moderate Match", "Low Match"]

    # Verify weights
    assert breakdown.required_skills.weight == 0.40
    assert breakdown.preferred_skills.weight == 0.20
    assert breakdown.semantic_similarity.weight == 0.20
    assert breakdown.title_experience_alignment.weight == 0.10
    assert breakdown.resume_completeness.weight == 0.10

    # Required score should be 3/4 = 75.0%
    assert breakdown.required_skills.raw_score == 75.0
    assert breakdown.required_skills.weighted_score == 30.0

    # Missing Docker should be in missing_required
    assert any(m.name == "Docker" for m in missing_req)

    # Suggestions check
    assert 3 <= len(suggestions) <= 6
    for s in suggestions:
        assert s.priority in ["High", "Medium", "Low"]
        assert len(s.title) > 0
        assert len(s.action) > 0


def test_missing_required_skills_reduces_score():
    profile = CandidateProfile(
        name="Candidate",
        email="c@example.com",
        phone="555-000-1111",
        detected_titles=["Software Engineer"]
    )

    req_skills_all = {
        "Python": {"category": "Languages"},
        "FastAPI": {"category": "Backend"},
        "Docker": {"category": "Cloud"},
        "Kubernetes": {"category": "Cloud"},
    }

    # Case 1: All 4 required skills present
    score_full, _, _, _, missing_full, _, _, _ = calculate_overall_match(
        resume_skills={"Python": {}, "FastAPI": {}, "Docker": {}, "Kubernetes": {}},
        req_skills=req_skills_all,
        pref_skills={},
        semantic_similarity=0.8,
        profile=profile,
        jd_text="Software Engineer",
        warnings=[],
        resume_text_len=800
    )

    # Case 2: Only 1 of 4 required skills present
    score_partial, _, _, _, missing_partial, _, _, _ = calculate_overall_match(
        resume_skills={"Python": {}},
        req_skills=req_skills_all,
        pref_skills={},
        semantic_similarity=0.8,
        profile=profile,
        jd_text="Software Engineer",
        warnings=[],
        resume_text_len=800
    )

    assert len(missing_full) == 0
    assert len(missing_partial) == 3
    # Missing required skills must significantly reduce the score
    assert score_partial < score_full
    assert (score_full - score_partial) >= 25.0
