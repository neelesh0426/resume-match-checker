import React from 'react';
import { Layers } from 'lucide-react';

export default function ScoreBreakdown({ breakdown }) {
  if (!breakdown) return null;

  const components = [
    { key: 'required_skills', data: breakdown.required_skills, color: '#f43f5e' },
    { key: 'preferred_skills', data: breakdown.preferred_skills, color: '#f59e0b' },
    { key: 'semantic_similarity', data: breakdown.semantic_similarity, color: '#6366f1' },
    { key: 'title_experience_alignment', data: breakdown.title_experience_alignment, color: '#0ea5e9' },
    { key: 'resume_completeness', data: breakdown.resume_completeness, color: '#10b981' },
  ].filter((c) => c.data);

  return (
    <div className="breakdown-section">
      <div className="section-header">
        <h2 className="section-title">Score Breakdown & Weighting</h2>
      </div>

      <div className="breakdown-grid">
        {components.map(({ key, data, color }) => {
          const rawScore = Math.round(data.raw_score * 10) / 10;
          const weightedScore = Math.round(data.weighted_score * 10) / 10;
          const weightPercent = Math.round(data.weight * 100);

          return (
            <div key={key} className="breakdown-card">
              <div className="breakdown-card-top">
                <span className="breakdown-category-title">{data.category}</span>
                <span className="breakdown-weight-badge">{weightPercent}% Weight</span>
              </div>

              <div className="breakdown-score-row">
                <span className="breakdown-raw-score">{rawScore}</span>
                <span className="breakdown-points-tag">+{weightedScore} pts</span>
              </div>

              <div className="component-progress-track">
                <div
                  className="component-progress-fill"
                  style={{
                    width: `${Math.min(100, Math.max(0, rawScore))}%`,
                    backgroundColor: color,
                  }}
                />
              </div>

              <p className="breakdown-card-expl">{data.explanation}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
