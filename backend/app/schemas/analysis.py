from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ScoreComponent(BaseModel):
    category: str
    weight: float = Field(..., description="Weight percentage (e.g. 0.40 for 40%)")
    raw_score: float = Field(..., description="Raw component score 0-100")
    weighted_score: float = Field(..., description="Weighted points contributed")
    explanation: str


class ScoreBreakdown(BaseModel):
    required_skills: ScoreComponent
    preferred_skills: ScoreComponent
    semantic_similarity: ScoreComponent
    title_experience_alignment: ScoreComponent
    resume_completeness: ScoreComponent


class MatchedSkill(BaseModel):
    name: str
    category: str
    matched_via: Optional[str] = None
    is_required: bool = True


class MissingSkill(BaseModel):
    name: str
    category: str
    is_required: bool = True


class ImprovementSuggestion(BaseModel):
    priority: str = Field(..., description="'High', 'Medium', or 'Low'")
    title: str
    action: str
    context: Optional[str] = None


class CandidateProfile(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    detected_titles: List[str] = []
    education: List[str] = []
    experience_indicators: List[str] = []
    total_experience_years: Optional[float] = None


class AnalysisResponse(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall transparent Resume Match Score 0-100")
    score_label: str = Field(..., description="Strong Match, Good Match, Moderate Match, or Low Match")
    score_breakdown: ScoreBreakdown
    matched_skills: List[MatchedSkill]
    missing_required_skills: List[MissingSkill]
    missing_preferred_skills: List[MissingSkill]
    semantic_similarity: float = Field(..., ge=0.0, le=1.0, description="Raw cosine semantic similarity 0.0-1.0")
    parsing_warnings: List[str] = []
    improvement_suggestions: List[ImprovementSuggestion]
    score_explanation: str
    candidate_profile: CandidateProfile
    processing_time_ms: float = 0.0


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
