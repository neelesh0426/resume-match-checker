/**
 * API Service for Resume Match Score Checker
 */

const API_BASE = '/api';

/**
 * Check backend health status
 * @returns {Promise<{status: string, service: string, version: string}>}
 */
export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) {
      throw new Error(`Health check returned status ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error('Backend health check failed:', err);
    throw err;
  }
}

/**
 * Upload resume file and job description to analyze match
 * @param {File} file - Resume file (.pdf or .docx)
 * @param {string} jobDescription - Plain text job description
 * @returns {Promise<any>} AnalysisResponse object
 */
export async function analyzeResume(file, jobDescription) {
  const formData = new FormData();
  formData.append('resume', file);
  formData.append('job_description', jobDescription.trim());

  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    let errorMessage = 'Failed to analyze resume.';
    if (data && data.detail) {
      if (Array.isArray(data.detail)) {
        errorMessage = data.detail.map((d) => d.msg || JSON.stringify(d)).join(', ');
      } else {
        errorMessage = data.detail;
      }
    }
    const error = new Error(errorMessage);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}
