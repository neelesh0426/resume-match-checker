import React from 'react';
import { Lightbulb, ArrowRight, ShieldCheck } from 'lucide-react';

export default function SuggestionsList({ suggestions = [] }) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="suggestions-card">
      <div className="section-header">
        <h2 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Lightbulb size={22} style={{ color: '#fbbf24' }} />
          Actionable ATS Optimization Tips
        </h2>
      </div>

      <div className="suggestions-list">
        {suggestions.map((item, idx) => (
          <div key={idx} className="suggestion-item">
            <span className={`suggestion-priority-tag ${item.priority}`}>
              {item.priority}
            </span>

            <div className="suggestion-body">
              <h3 className="suggestion-title">{item.title}</h3>
              <p className="suggestion-action">{item.action}</p>
              {item.context && <p className="suggestion-context">{item.context}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
