import os
import re
import logging
from typing import Tuple, List
import pdfplumber
import docx
from app.config import settings

logger = logging.getLogger(__name__)


def clean_extracted_text(text: str) -> str:
    """Normalize whitespace and line breaks while preserving paragraph boundaries."""
    if not text:
        return ""
    # Normalize multiple carriage returns / tabs
    text = re.sub(r"\r\n|\r", "\n", text)
    # Remove control characters except newline and tab
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
    # Normalize excessive blank lines (more than 2 to 2)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Normalize horizontal spaces
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def extract_text_from_pdf(file_path: str) -> Tuple[str, List[str]]:
    """Extract text from a PDF file using pdfplumber, with graceful OCR fallback for scanned pages."""
    warnings: List[str] = []
    extracted_pages: List[str] = []

    try:
        with pdfplumber.open(file_path) as pdf:
            if not pdf.pages:
                raise ValueError("The uploaded PDF has 0 pages.")
            
            for page_idx, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                # Also check for table text if standard extract is sparse
                if not page_text.strip():
                    tables = page.extract_tables() or []
                    for table in tables:
                        table_lines = ["\t".join(filter(None, [str(c or '').strip() for c in row])) for row in table]
                        page_text += "\n" + "\n".join(table_lines)
                
                extracted_pages.append(page_text.strip())

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        logger.error(f"pdfplumber failed to parse PDF: {e}")
        raise ValueError(f"Malformed or corrupted PDF file: {str(e)}")

    full_text = "\n\n".join(filter(None, extracted_pages)).strip()

    # If text is extremely short or blank, try OCR fallback
    if len(full_text.replace(" ", "")) < 50 and settings.ocr_enabled:
        logger.info("PDF contains minimal or no text layer. Attempting OCR fallback...")
        ocr_text, ocr_warning = _try_ocr_fallback(file_path)
        if ocr_text:
            full_text = ocr_text
            warnings.append(
                "Text was recovered using OCR from scanned pages. Formatting and special characters may vary."
            )
        elif ocr_warning:
            warnings.append(ocr_warning)

    full_text = clean_extracted_text(full_text)
    if not full_text:
        raise ValueError("Could not extract any readable text from this PDF. The document may be blank or an unreadable scanned image.")

    return full_text, warnings


def _try_ocr_fallback(file_path: str) -> Tuple[str, str]:
    """Attempt OCR extraction using pdf2image and pytesseract.
    Returns (extracted_text, warning_message). Never raises fatal exceptions.
    """
    try:
        import pytesseract
        from pdf2image import convert_from_path

        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

        poppler_kwargs = {}
        if settings.poppler_path:
            poppler_kwargs["poppler_path"] = settings.poppler_path

        # Convert up to the first 4 pages to avoid high memory/time spikes
        images = convert_from_path(file_path, first_page=1, last_page=4, dpi=200, **poppler_kwargs)
        ocr_pages: List[str] = []
        for img in images:
            text = pytesseract.image_to_string(img)
            if text.strip():
                ocr_pages.append(text.strip())

        combined_text = "\n\n".join(ocr_pages).strip()
        if combined_text:
            return combined_text, ""
        return "", "OCR fallback executed but detected no readable text on the scanned pages."

    except Exception as exc:
        logger.info(f"OCR fallback unavailable: {exc}")
        return "", (
            "Document appears to be a scanned image or non-text PDF. "
            "Text layer was empty, and OCR fallback was unavailable in the current system environment."
        )


def extract_text_from_docx(file_path: str) -> Tuple[str, List[str]]:
    """Extract text from a Word DOCX file using python-docx."""
    warnings: List[str] = []
    paragraphs_text: List[str] = []

    try:
        doc = docx.Document(file_path)
        # Extract normal paragraphs
        for p in doc.paragraphs:
            if p.text.strip():
                paragraphs_text.append(p.text.strip())

        # Extract text inside tables
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    paragraphs_text.append(" | ".join(row_cells))

    except Exception as e:
        logger.error(f"python-docx failed to parse DOCX: {e}")
        raise ValueError(f"Malformed or corrupted DOCX file: {str(e)}")

    full_text = clean_extracted_text("\n\n".join(paragraphs_text))
    if not full_text:
        raise ValueError("Could not extract any readable text from this DOCX file. The document appears to be empty.")

    return full_text, warnings


def parse_resume_file(file_path: str, filename: str) -> Tuple[str, List[str]]:
    """Dispatch file parsing based on extension (.pdf or .docx)."""
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Only PDF (.pdf) and Word (.docx) files are supported.")
