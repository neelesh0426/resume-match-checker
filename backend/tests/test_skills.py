from app.services.skills import (
    extract_skills_from_text,
    extract_jd_skills,
    segment_job_description,
    SKILLS_TAXONOMY
)


def test_alias_resolution_js_ts_postgres_aws():
    text = "Proficient in JS and TS, with extensive Postgres database and AWS cloud experience."
    skills = extract_skills_from_text(text)

    assert "JavaScript" in skills
    assert "TypeScript" in skills
    assert "PostgreSQL" in skills
    assert "Amazon Web Services" in skills


def test_alias_resolution_k8s_reactjs_node():
    text = "Deployed microservices on K8s cluster with Node backend and ReactJS frontend."
    skills = extract_skills_from_text(text)

    assert "Kubernetes" in skills
    assert "Node.js" in skills
    assert "React" in skills
    assert "Microservices" in skills


def test_ai_ml_skills_extraction():
    text = "Experience with Python, PyTorch, TensorFlow, Scikit-learn, and Natural Language Processing."
    skills = extract_skills_from_text(text)

    assert "Python" in skills
    assert "PyTorch" in skills
    assert "TensorFlow" in skills
    assert "Scikit-learn" in skills
    assert "Natural Language Processing" in skills


def test_segment_job_description():
    jd = """
    Software Engineer
    Required Qualifications:
    - Experience with Python and Docker
    Preferred Qualifications:
    - Experience with Kubernetes and Redis
    """
    req_sec, pref_sec, gen_sec = segment_job_description(jd)
    assert "Python" in req_sec
    assert "Kubernetes" in pref_sec


def test_extract_jd_skills_required_vs_preferred():
    jd = """
    Backend Engineer
    Required Qualifications:
    - Strong knowledge of Python and FastAPI
    - Experience with PostgreSQL

    Preferred Qualifications:
    - Familiarity with Docker and Redis
    """
    req, pref = extract_jd_skills(jd)
    assert "Python" in req
    assert "FastAPI" in req
    assert "PostgreSQL" in req
    assert "Docker" in pref
    assert "Redis" in pref
