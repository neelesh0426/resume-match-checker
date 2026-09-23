import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ResumeUploader from './components/ResumeUploader';
import JobDescriptionInput from './components/JobDescriptionInput';
import CircularScoreGauge from './components/CircularScoreGauge';
import ScoreBreakdown from './components/ScoreBreakdown';
import SkillsMatrix from './components/SkillsMatrix';
import SuggestionsList from './components/SuggestionsList';
import CandidateSummary from './components/CandidateSummary';
import LoadingOverlay from './components/LoadingOverlay';
import { analyzeResume, checkHealth } from './services/api';
import { ArrowRight, RotateCcw, AlertTriangle, Sparkles } from 'lucide-react';

export default function App() {
  const [file, setFile] = useState(null);
  const [jdText, setJdText] = useState('');
  const [fileError, setFileError] = useState(null);
  const [apiError, setApiError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [isBackendOnline, setIsBackendOnline] = useState(false);

  // Poll backend health status on mount
  useEffect(() => {
    let isMounted = true;
    const verifyHealth = async () => {
      try {
        await checkHealth();
        if (isMounted) setIsBackendOnline(true);
      } catch (err) {
        if (isMounted) setIsBackendOnline(false);
      }
    };

    verifyHealth();
    const interval = setInterval(verifyHealth, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const canAnalyze = !!file && jdText.trim().length >= 30 && !isLoading;

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!canAnalyze) return;

    setApiError(null);
    setIsLoading(true);

    try {
      const data = await analyzeResume(file, jdText);
      setResult(data);
      // Smooth scroll to top of results
      window.scrollTo({ top: 320, behavior: 'smooth' });
    } catch (err) {
      setApiError(err.message || 'Error communicating with analysis service.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setApiError(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div>
      <Navbar isBackendOnline={isBackendOnline} />

      <main className="app-container">
        {/* Hero Section */}
        <section className="hero-section">
          <div className="hero-pill">
            <Sparkles size={14} /> AI-Powered Semantic ATS Analyzer
          </div>
          <h1 className="hero-title">
            Optimize Your Resume with <span className="hero-title-gradient">Transparent AI Scoring</span>
          </h1>
          <p className="hero-description">
            Get an instant, explainable 0–100 match score with multi-dimensional weighting, keyword gap analysis, and tailored ATS optimization advice.
          </p>
        </section>

        {/* Input Workspace Form */}
        <form onSubmit={handleAnalyze}>
          <div className="workspace-grid">
            <ResumeUploader
              file={file}
              setFile={setFile}
              error={fileError}
              setError={setFileError}
            />

            <JobDescriptionInput
              jdText={jdText}
              setJdText={setJdText}
            />
          </div>

          {/* Primary Call to Action */}
          <div className="action-bar">
            {apiError && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fb7185', background: 'rgba(244, 63, 94, 0.1)', padding: '0.75rem 1.25rem', borderRadius: '12px', border: '1px solid rgba(244, 63, 94, 0.3)' }}>
                <AlertTriangle size={18} />
                <span>{apiError}</span>
              </div>
            )}

            {!isLoading && (
              <button
                type="submit"
                className="btn-primary-glow"
                disabled={!canAnalyze}
              >
                <span>Analyze Resume Match</span>
                <ArrowRight size={20} />
              </button>
            )}

            {!canAnalyze && !isLoading && (
              <span className="action-hint">
                {!file
                  ? 'Attach a resume (.pdf or .docx) to proceed'
                  : jdText.trim().length < 30
                  ? 'Provide a job description with at least 30 characters'
                  : ''}
              </span>
            )}
          </div>
        </form>

        {/* Loading Indicator */}
        {isLoading && <LoadingOverlay />}

        {/* Results Dashboard */}
        {result && !isLoading && (
          <section className="results-wrapper">
            {/* Candidate summary info if detected */}
            <CandidateSummary profile={result.candidate_profile} />

            {/* Parsing Warnings Alert if any */}
            {result.parsing_warnings && result.parsing_warnings.length > 0 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.85rem 1.25rem', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.25)', borderRadius: '12px', color: '#fbbf24', fontSize: '0.875rem' }}>
                <AlertTriangle size={18} />
                <span>{result.parsing_warnings.join(' • ')}</span>
              </div>
            )}

            {/* Circular Gauge & Hero Summary */}
            <CircularScoreGauge
              score={result.overall_score}
              scoreLabel={result.score_label}
              processingTimeMs={result.processing_time_ms}
              explanation={result.score_explanation}
            />

            {/* Score Breakdown (5 Components) */}
            <ScoreBreakdown breakdown={result.score_breakdown} />

            {/* Skills & Keyword Match Matrix */}
            <SkillsMatrix
              matchedSkills={result.matched_skills}
              missingRequired={result.missing_required_skills}
              missingPreferred={result.missing_preferred_skills}
            />

            {/* Actionable Improvement Tips */}
            <SuggestionsList suggestions={result.improvement_suggestions} />

            {/* Reset / Scan Another Button */}
            <div className="bottom-action-bar">
              <button type="button" className="btn-secondary" onClick={handleReset}>
                <RotateCcw size={16} /> Scan Another Resume
              </button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
