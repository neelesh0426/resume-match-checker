import os
import tempfile
import pytest
from app.services.parser import (
    parse_resume_file,
    clean_extracted_text,
    extract_text_from_docx,
    extract_text_from_pdf
)


def test_clean_extracted_text():
    raw = "  Hello \r\n\r\n\r\n World! \t\t Testing   spaces.  "
    cleaned = clean_extracted_text(raw)
    assert "Hello" in cleaned
    assert "World!" in cleaned
    assert "Testing spaces." in cleaned
    assert "\r" not in cleaned


def test_unsupported_file_extension():
    with pytest.raises(ValueError) as exc:
        parse_resume_file("fake.txt", "resume.txt")
    assert "Unsupported file format" in str(exc.value)


def test_parse_valid_docx(sample_docx_bytes):
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(sample_docx_bytes)
        tmp_path = tmp.name

    try:
        text, warnings = parse_resume_file(tmp_path, "sample.docx")
        assert len(text) > 50
        assert "Alex Morgan" in text
        assert "React" in text
        assert "PostgreSQL" in text
        assert isinstance(warnings, list)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_parse_valid_pdf(sample_pdf_bytes):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(sample_pdf_bytes)
        tmp_path = tmp.name

    try:
        text, warnings = parse_resume_file(tmp_path, "sample.pdf")
        assert len(text) > 30
        assert "Alex Morgan" in text
        assert "TypeScript" in text
        assert isinstance(warnings, list)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_empty_docx_raises_value_error():
    # Write empty file
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        with pytest.raises(ValueError):
            parse_resume_file(tmp_path, "empty.docx")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_corrupted_pdf_raises_value_error():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(b"NOT A REAL PDF FILE CONTENT 12345")
        tmp_path = tmp.name

    try:
        with pytest.raises(ValueError):
            parse_resume_file(tmp_path, "corrupted.pdf")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
