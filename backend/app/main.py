import os
import time
import tempfile
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, get_db
from app.models.analysis import AnalysisRecord
from app.schemas.analysis import AnalysisResponse, ErrorResponse
from app.services.parser import parse_resume_file
from app.services.extractor import extract_candidate_profile
from app.services.skills import extract_skills_from_text, extract_jd_skills
from app.services.matcher import compute_overall_semantic_similarity
from app.services.scorer import calculate_overall_match

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("resume_checker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created.")
    logger.info(f"CORS origins configured: {settings.get_cors_origins()}")
    yield
    # Shutdown logic if any
    logger.info("Shutting down Resume Match Score Checker service.")


app = FastAPI(
    title="Resume Match Score Checker API",
    description="Analyzes resumes against job descriptions with transparent, explainable 0-100 scoring.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS restricted to frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend status."""
    return {
        "status": "healthy",
        "service": "Resume Match Score Checker",
        "version": "1.0.0"
    }


@app.post(
    "/api/analyze",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input, file format, or empty document"},
        413: {"model": ErrorResponse, "description": "File exceeds maximum upload size"},
        500: {"model": ErrorResponse, "description": "Internal processing error"}
    },
    tags=["Analysis"]
)
async def analyze_resume(
    resume: UploadFile = File(..., description="Resume file (.pdf or .docx), max 10MB"),
    job_description: str = Form("", description="Required plain-text job description"),
    db: Session = Depends(get_db)
):
    """Analyze an uploaded PDF/DOCX resume against a job description.
    Resumes are processed in temporary storage and deleted immediately.
    """
    start_time = time.time()
    temp_file_path: Optional[str] = None

    # 1. Validate Job Description
    if not job_description or not job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description cannot be empty. Please paste the job description text."
        )

    clean_jd = job_description.strip()
    if len(clean_jd) < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is too brief. Please provide a more complete job description (at least 30 characters)."
        )

    # 2. Validate File Name and Extension
    filename = resume.filename or ""
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{file_ext}'. Please upload a PDF (.pdf) or Word (.docx) document."
        )

    try:
        # 3. Create temporary file and stream content safely
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            temp_file_path = tmp.name
            total_bytes = 0
            chunk_size = 1024 * 64  # 64 KB chunks

            while chunk := await resume.read(chunk_size):
                total_bytes += len(chunk)
                if total_bytes > settings.max_file_size_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds maximum allowed size of {settings.max_file_size_mb} MB."
                    )
                tmp.write(chunk)

        if total_bytes == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded resume file is completely empty (0 bytes)."
            )

        # 4. Parse Resume Text
        try:
            resume_text, parsing_warnings = parse_resume_file(temp_file_path, filename)
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )

        # 5. Extract Candidate Profile
        profile = extract_candidate_profile(resume_text)

        # 6. Extract Skills from Resume and Job Description
        resume_skills = extract_skills_from_text(resume_text)
        req_skills, pref_skills = extract_jd_skills(clean_jd)

        # 7. Compute Semantic Similarity
        semantic_sim = compute_overall_semantic_similarity(resume_text, clean_jd)

        # 8. Calculate Overall Score & Breakdown
        (
            overall_score,
            score_label,
            breakdown,
            matched_skills,
            missing_req,
            missing_pref,
            suggestions,
            score_explanation
        ) = calculate_overall_match(
            resume_skills=resume_skills,
            req_skills=req_skills,
            pref_skills=pref_skills,
            semantic_similarity=semantic_sim,
            profile=profile,
            jd_text=clean_jd,
            warnings=parsing_warnings,
            resume_text_len=len(resume_text)
        )

        processing_time_ms = round((time.time() - start_time) * 1000, 1)

        # 9. Record non-sensitive metadata audit record
        try:
            audit_record = AnalysisRecord(
                overall_score=overall_score,
                score_label=score_label,
                matched_skills_count=len(matched_skills),
                missing_required_count=len(missing_req),
                missing_preferred_count=len(missing_pref),
                semantic_similarity=semantic_sim,
                processing_time_ms=processing_time_ms
            )
            db.add(audit_record)
            db.commit()
        except Exception as db_err:
            logger.warning(f"Could not write audit record: {db_err}")
            db.rollback()

        return AnalysisResponse(
            overall_score=overall_score,
            score_label=score_label,
            score_breakdown=breakdown,
            matched_skills=matched_skills,
            missing_required_skills=missing_req,
            missing_preferred_skills=missing_pref,
            semantic_similarity=semantic_sim,
            parsing_warnings=parsing_warnings,
            improvement_suggestions=suggestions,
            score_explanation=score_explanation,
            candidate_profile=profile,
            processing_time_ms=processing_time_ms
        )

    finally:
        # GUARANTEE: Never persist uploaded resume on disk
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.debug(f"Securely deleted temporary resume file: {temp_file_path}")
            except Exception as cleanup_err:
                logger.warning(f"Failed to delete temp file {temp_file_path}: {cleanup_err}")
