import io
import sys
from pathlib import Path

# Ensure the backend directory is in sys.path for direct pytest invocation
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from docx import Document
from app.main import app

SAMPLE_JD = """
Senior Full Stack Developer

About Us:
We are seeking an experienced Senior Full Stack Developer to lead our core product engineering team.

Required Qualifications:
- 4+ years of professional software engineering experience
- Strong proficiency in TypeScript, React, and Node.js
- Production experience with PostgreSQL and Docker
- Demonstrated experience designing REST APIs and microservices

Preferred Qualifications:
- Experience with Amazon Web Services (AWS) or Kubernetes
- Familiarity with GraphQL and Redis caching
- Background in Agile / Scrum methodologies

Responsibilities:
- Build high-performance scalable web applications
- Collaborate with product designers and backend engineers
"""

SAMPLE_RESUME_TEXT = """
Alex Morgan
alex.morgan@example.com | (555) 234-5678 | linkedin.com/in/alexmorgan | github.com/alexmorgan
San Francisco, CA

PROFESSIONAL SUMMARY
Senior Full Stack Engineer with 5+ years of experience building modern web applications with React, TypeScript, Node.js, and PostgreSQL.

TECHNICAL SKILLS
Languages: TypeScript, JavaScript, Python, SQL, HTML/CSS
Frontend: React, Next.js, Redux, Tailwind CSS
Backend & Databases: Node.js, Express.js, PostgreSQL, Redis, REST APIs
DevOps & Tools: Docker, AWS, Git, CI/CD

EXPERIENCE
Senior Software Engineer | CloudTech Solutions (2021 - Present)
- Engineered scalable full stack microservices using React, TypeScript, Node.js, and PostgreSQL.
- Implemented automated CI/CD deployment pipelines using Docker and AWS.

Software Developer | Horizon Labs (2018 - 2021)
- Developed responsive frontends using React and JavaScript.
- Built backend REST APIs and integrated SQL databases.

EDUCATION
Bachelor of Science in Computer Science | University of California, Berkeley (2018)
"""


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_docx_bytes():
    doc = Document()
    doc.add_heading("Alex Morgan", 0)
    doc.add_paragraph("alex.morgan@example.com | (555) 234-5678 | linkedin.com/in/alexmorgan | github.com/alexmorgan")
    doc.add_heading("Summary", level=1)
    doc.add_paragraph("Senior Full Stack Engineer with 5+ years of experience building scalable applications.")
    doc.add_heading("Skills", level=1)
    doc.add_paragraph("JavaScript, TypeScript, React, Node.js, PostgreSQL, Docker, AWS, Git")
    doc.add_heading("Experience", level=1)
    doc.add_paragraph("Senior Software Engineer at Tech Corp (2020 - Present)")
    doc.add_heading("Education", level=1)
    doc.add_paragraph("Bachelor of Science in Computer Science (2020)")

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


@pytest.fixture
def sample_pdf_bytes():
    # Construct a minimal standard conforming PDF with a text stream
    content = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        b"5 0 obj << /Length 200 >> stream\n"
        b"BT\n"
        b"/F1 12 Tf\n"
        b"72 712 Td\n"
        b"(Alex Morgan) Tj ET\n"
        b"BT /F1 10 Tf 72 690 Td (alex.morgan@example.com | 555-123-4567 | linkedin.com/in/alexmorgan) Tj ET\n"
        b"BT /F1 10 Tf 72 670 Td (Senior Software Engineer with 5 years experience) Tj ET\n"
        b"BT /F1 10 Tf 72 650 Td (Skills: TypeScript, React, Node.js, PostgreSQL, Docker, AWS) Tj ET\n"
        b"BT /F1 10 Tf 72 630 Td (Bachelor of Science in Computer Science 2019) Tj ET\n"
        b"endstream\n"
        b"endobj\n"
        b"xref\n"
        b"0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000244 00000 n \n"
        b"0000000318 00000 n \n"
        b"trailer << /Size 6 /Root 1 0 R >>\n"
        b"startxref\n"
        b"570\n"
        b"%%EOF\n"
    )
    return content
