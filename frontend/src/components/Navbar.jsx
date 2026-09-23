import React from 'react';
import { FileCheck2, Cpu } from 'lucide-react';

export default function Navbar({ isBackendOnline }) {
  return (
    <header className="navbar">
      <div className="brand-wrapper">
        <div className="brand-icon-box">
          <FileCheck2 size={24} strokeWidth={2.2} />
        </div>
        <div className="brand-text">
          <span className="brand-title">ResumeMatch</span>
          <span className="brand-subtitle">Explainable ATS Scoring Engine</span>
        </div>
      </div>

      <div className="nav-actions">
        <div className={`status-badge ${isBackendOnline ? 'online' : 'offline'}`}>
          <span className="status-dot"></span>
          <span>{isBackendOnline ? 'AI Engine Online' : 'Engine Connecting...'}</span>
        </div>
      </div>
    </header>
  );
}
