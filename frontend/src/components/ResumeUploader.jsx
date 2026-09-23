import React, { useRef, useState } from 'react';
import { UploadCloud, FileText, X, AlertCircle } from 'lucide-react';

export default function ResumeUploader({ file, setFile, error, setError }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef(null);

  const MAX_SIZE_MB = 10;
  const ALLOWED_EXTS = ['.pdf', '.docx'];

  const validateAndSetFile = (selectedFile) => {
    if (!selectedFile) return;

    const fileName = selectedFile.name.toLowerCase();
    const hasValidExt = ALLOWED_EXTS.some((ext) => fileName.endsWith(ext));

    if (!hasValidExt) {
      setError(`Invalid file format. Please upload a PDF (.pdf) or Word document (.docx).`);
      return;
    }

    if (selectedFile.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`File is too large (${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB). Maximum allowed is ${MAX_SIZE_MB} MB.`);
      return;
    }

    setError(null);
    setFile(selectedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="panel-card">
      <div className="panel-header">
        <div className="panel-title-group">
          <div className="panel-icon-wrap">
            <FileText size={18} />
          </div>
          <h2 className="panel-title">1. Upload Resume</h2>
        </div>
        <span className="panel-badge">PDF or DOCX</span>
      </div>

      {!file ? (
        <div
          className={`dropzone ${isDragOver ? 'active' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            type="file"
            ref={inputRef}
            onChange={handleFileChange}
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            style={{ display: 'none' }}
          />
          <div className="dropzone-icon">
            <UploadCloud size={28} />
          </div>
          <p className="dropzone-title">Click to upload or drag & drop</p>
          <p className="dropzone-sub">Supports PDF (.pdf) and Microsoft Word (.docx)</p>
          <span className="dropzone-meta">Max file size: 10 MB • Text sanitized in-memory</span>
        </div>
      ) : (
        <div className="selected-file-card">
          <div className="selected-file-icon">
            <FileText size={26} />
          </div>
          <span className="selected-file-name">{file.name}</span>
          <span className="selected-file-size">{formatFileSize(file.size)}</span>
          <button
            type="button"
            className="remove-file-btn"
            onClick={() => {
              setFile(null);
              setError(null);
            }}
          >
            <X size={14} /> Remove File
          </button>
        </div>
      )}

      {error && (
        <div style={{ marginTop: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#fb7185', fontSize: '0.85rem' }}>
          <AlertCircle size={15} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
