from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime
from app.database import Base


class AnalysisRecord(Base):
    """Metadata-only audit record of an analysis session.
    Never persists resume file text or candidate personal data.
    """
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    overall_score = Column(Float, nullable=False)
    score_label = Column(String(50), nullable=False)
    matched_skills_count = Column(Integer, default=0)
    missing_required_count = Column(Integer, default=0)
    missing_preferred_count = Column(Integer, default=0)
    semantic_similarity = Column(Float, default=0.0)
    processing_time_ms = Column(Float, default=0.0)
