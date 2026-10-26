import React from 'react';

/**
 * SummaryCards Component
 * Metric stat cards displaying key totals across the candidate pipeline:
 * Total Screened, Successfully Processed, In Processing, and Action Needed.
 */
export default function SummaryCards({ candidates = [] }) {
  const total = candidates.length;
  const completed = candidates.filter(
    (c) => (c.status || '').toUpperCase() === 'COMPLETED'
  ).length;
  const inPipeline = candidates.filter((c) => {
    const s = (c.status || '').toUpperCase();
    return s === 'PROCESSING' || s === 'UPLOADING';
  }).length;
  const failed = candidates.filter(
    (c) => (c.status || '').toUpperCase() === 'FAILED'
  ).length;

  return (
    <div className="summary-cards-grid">
      {/* Total Candidates Card */}
      <div className="summary-card card-total">
        <div className="summary-card-header">
          <span className="summary-card-title">Total Candidates</span>
          <span className="summary-card-icon">👥</span>
        </div>
        <div className="summary-card-body">
          <span className="summary-value">{total}</span>
          <span className="summary-subtitle">Resumes in pool</span>
        </div>
      </div>

      {/* Completed Candidates Card */}
      <div className="summary-card card-completed">
        <div className="summary-card-header">
          <span className="summary-card-title">Completed & Analyzed</span>
          <span className="summary-card-icon text-success">✓</span>
        </div>
        <div className="summary-card-body">
          <span className="summary-value text-success">{completed}</span>
          <span className="summary-subtitle">Ready for job matching</span>
        </div>
      </div>

      {/* Processing Pipeline Card */}
      <div className="summary-card card-processing">
        <div className="summary-card-header">
          <span className="summary-card-title">In Pipeline</span>
          <span className="summary-card-icon text-warning">⚡</span>
        </div>
        <div className="summary-card-body">
          <span className="summary-value text-warning">{inPipeline}</span>
          <span className="summary-subtitle">Parsing & OCR in progress</span>
        </div>
      </div>

      {/* Failed / Action Needed Card */}
      <div className="summary-card card-failed">
        <div className="summary-card-header">
          <span className="summary-card-title">Failed / Issues</span>
          <span className="summary-card-icon text-danger">⚠️</span>
        </div>
        <div className="summary-card-body">
          <span className="summary-value text-danger">{failed}</span>
          <span className="summary-subtitle">Require re-upload</span>
        </div>
      </div>
    </div>
  );
}
