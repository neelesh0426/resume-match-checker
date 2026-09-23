import io
from tests.conftest import SAMPLE_JD


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_analyze_valid_docx(client, sample_docx_bytes):
    response = client.post(
        "/api/analyze",
        files={"resume": ("test_resume.docx", io.BytesIO(sample_docx_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        data={"job_description": SAMPLE_JD}
    )
    assert response.status_code == 200
    data = response.json()

    # Verify structured response attributes
    assert "overall_score" in data
    assert 0.0 <= data["overall_score"] <= 100.0
    assert data["score_label"] in ["Strong Match", "Good Match", "Moderate Match", "Low Match"]
    assert "score_breakdown" in data
    assert "matched_skills" in data
    assert "missing_required_skills" in data
    assert "missing_preferred_skills" in data
    assert "semantic_similarity" in data
    assert "improvement_suggestions" in data
    assert 3 <= len(data["improvement_suggestions"]) <= 6
    assert "candidate_profile" in data
    assert data["candidate_profile"]["name"] == "Alex Morgan"


def test_analyze_missing_job_description(client, sample_docx_bytes):
    response = client.post(
        "/api/analyze",
        files={"resume": ("test_resume.docx", io.BytesIO(sample_docx_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        data={"job_description": ""}
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "empty" in data["detail"].lower()


def test_analyze_unsupported_file_extension(client):
    response = client.post(
        "/api/analyze",
        files={"resume": ("test_resume.txt", io.BytesIO(b"Plain text resume content"), "text/plain")},
        data={"job_description": SAMPLE_JD}
    )
    assert response.status_code == 400
    data = response.json()
    assert "Unsupported file extension" in data["detail"]


def test_analyze_empty_file(client):
    response = client.post(
        "/api/analyze",
        files={"resume": ("empty.docx", io.BytesIO(b""), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        data={"job_description": SAMPLE_JD}
    )
    assert response.status_code == 400
    data = response.json()
    assert "empty" in data["detail"].lower()
