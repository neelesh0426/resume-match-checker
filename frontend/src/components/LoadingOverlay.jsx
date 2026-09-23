import React, { useEffect, useState } from 'react';

const STAGES = [
  { title: 'Reading & Sanitizing Resume...', sub: 'Extracting text sections via pdfplumber / python-docx' },
  { title: 'Analyzing Skill Taxonomy...', sub: 'Running spaCy PhraseMatcher & fuzzy alias detection' },
  { title: 'Computing Vector Embeddings...', sub: 'Evaluating cosine similarity with all-MiniLM-L6-v2' },
  { title: 'Calculating ATS Match Score...', sub: 'Applying weighted scoring dimensions & generating tips' },
];

export default function LoadingOverlay() {
  const [currentStageIdx, setCurrentStageIdx] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStageIdx((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 1800);

    return () => clearInterval(timer);
  }, []);

  const stage = STAGES[currentStageIdx];

  return (
    <div className="loading-container">
      <div className="spinner-ring"></div>
      <h3 className="loading-step-title">{stage.title}</h3>
      <p className="loading-step-sub">{stage.sub}</p>
      <div className="loading-progress-track">
        <div className="loading-progress-bar"></div>
      </div>
    </div>
  );
}
