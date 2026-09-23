import React from 'react';
import { Award, Zap, CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';

export default function CircularScoreGauge({ score, scoreLabel, processingTimeMs, explanation }) {
  const roundedScore = Math.round(score * 10) / 10;
  const radius = 80;
  const stroke = 12;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (Math.min(100, Math.max(0, roundedScore)) / 100) * circumference;

  const getScoreTheme = (val) => {
    if (val >= 75) {
      return {
        color: '#10b981',
        className: 'strong',
        icon: CheckCircle2,
      };
    }
    if (val >= 60) {
      return {
        color: '#0ea5e9',
        className: 'good',
        icon: Award,
      };
    }
    if (val >= 45) {
      return {
        color: '#f59e0b',
        className: 'moderate',
        icon: AlertTriangle,
      };
    }
    return {
      color: '#f43f5e',
      className: 'low',
      icon: XCircle,
    };
  };

  const theme = getScoreTheme(roundedScore);
  const StatusIcon = theme.icon;

  return (
    <div className="results-hero-card">
      <div className="gauge-container">
        <div className="circular-gauge">
          <svg
            className="gauge-svg"
            height={radius * 2}
            width={radius * 2}
            viewBox={`0 0 ${radius * 2} ${radius * 2}`}
          >
            <circle
              className="gauge-bg"
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
            <circle
              className="gauge-progress"
              stroke={theme.color}
              strokeDasharray={`${circumference} ${circumference}`}
              style={{ strokeDashoffset }}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
          </svg>
          <div className="gauge-center-content">
            <span className="gauge-score-number" style={{ color: theme.color }}>
              {roundedScore}
            </span>
            <span className="gauge-score-label">out of 100</span>
          </div>
        </div>
      </div>

      <div className="results-summary-right">
        <div className="score-badge-row">
          <span className={`score-badge-pill ${theme.className}`}>
            <StatusIcon size={18} />
            {scoreLabel}
          </span>
          {processingTimeMs > 0 && (
            <span className="execution-time-tag">
              <Zap size={13} /> Processed in {(processingTimeMs / 1000).toFixed(2)}s
            </span>
          )}
        </div>

        <p className="score-explanation-text">
          {explanation}
        </p>
      </div>
    </div>
  );
}
