import React from 'react';
import { CheckCircle2, AlertOctagon, HelpCircle, Tags } from 'lucide-react';

export default function SkillsMatrix({
  matchedSkills = [],
  missingRequired = [],
  missingPreferred = []
}) {
  return (
    <div className="skills-matrix-card">
      <div className="skills-matrix-header">
        <h2 className="section-title">Skills & Keyword Match Matrix</h2>
        <div className="matrix-counts">
          <span className="count-indicator matched">
            <CheckCircle2 size={15} /> {matchedSkills.length} Matched
          </span>
          <span className="count-indicator required">
            <AlertOctagon size={15} /> {missingRequired.length} Missing Core
          </span>
          <span className="count-indicator preferred">
            <HelpCircle size={15} /> {missingPreferred.length} Missing Preferred
          </span>
        </div>
      </div>

      <div className="skills-group-container">
        {/* Matched Skills */}
        <div>
          <h3 className="skills-subgroup-title" style={{ color: '#34d399' }}>
            <CheckCircle2 size={16} /> Matched Skills Found in Resume ({matchedSkills.length})
          </h3>
          {matchedSkills.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', fontStyle: 'italic' }}>
              No explicit skill keywords from the job description were detected in the resume text.
            </p>
          ) : (
            <div className="skills-badge-wrap">
              {matchedSkills.map((skill, idx) => (
                <span key={`${skill.name}-${idx}`} className="skill-pill matched">
                  <CheckCircle2 size={13} />
                  <span>{skill.name}</span>
                  {skill.category && <span className="skill-category-tag">{skill.category}</span>}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Missing Required Skills */}
        <div>
          <h3 className="skills-subgroup-title" style={{ color: '#fb7185' }}>
            <AlertOctagon size={16} /> Missing Required Skills ({missingRequired.length})
          </h3>
          {missingRequired.length === 0 ? (
            <p style={{ color: '#34d399', fontSize: '0.9rem' }}>
              Awesome! Your resume covers all core required skills detected in the job description.
            </p>
          ) : (
            <div className="skills-badge-wrap">
              {missingRequired.map((skill, idx) => (
                <span key={`${skill.name}-${idx}`} className="skill-pill missing-required">
                  <AlertOctagon size={13} />
                  <span>{skill.name}</span>
                  {skill.category && <span className="skill-category-tag">{skill.category}</span>}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Missing Preferred Skills */}
        {missingPreferred.length > 0 && (
          <div>
            <h3 className="skills-subgroup-title" style={{ color: '#fbbf24' }}>
              <HelpCircle size={16} /> Missing Preferred / Nice-to-Have Skills ({missingPreferred.length})
            </h3>
            <div className="skills-badge-wrap">
              {missingPreferred.map((skill, idx) => (
                <span key={`${skill.name}-${idx}`} className="skill-pill missing-preferred">
                  <HelpCircle size={13} />
                  <span>{skill.name}</span>
                  {skill.category && <span className="skill-category-tag">{skill.category}</span>}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
