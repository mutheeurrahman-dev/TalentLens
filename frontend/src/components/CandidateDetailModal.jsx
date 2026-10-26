import React, { useState } from 'react';
import StatusBadge from './StatusBadge.jsx';

/**
 * CandidateDetailModal Component
 * Modal dialog displaying detailed candidate information, matched skills,
 * missing skills, and the full extracted resume text with copy action.
 */
export default function CandidateDetailModal({ candidate, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!candidate) return null;

  const {
    candidateId,
    candidateName,
    filename,
    status,
    createdAt,
    processedAt,
    resumeText,
    matchResult,
    errorMessage,
  } = candidate;

  const displayName = candidateName || filename || `Candidate #${candidateId?.slice(0, 8)}`;
  const matchPercentage = matchResult?.matchPercentage;

  const handleCopyText = () => {
    if (!resumeText) return;
    navigator.clipboard.writeText(resumeText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const formatDate = (isoStr) => {
    if (!isoStr) return 'N/A';
    try {
      return new Date(isoStr).toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short',
      });
    } catch (_) {
      return isoStr;
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-title-group">
            <div className="modal-avatar">
              {(displayName || 'C').charAt(0).toUpperCase()}
            </div>
            <div>
              <h2 className="modal-title">{displayName}</h2>
              <p className="modal-subtitle">
                <span>📄 {filename}</span>
                <span className="dot-separator">•</span>
                <span>ID: {candidateId?.slice(0, 8)}</span>
              </p>
            </div>
          </div>
          <div className="modal-header-actions">
            <StatusBadge status={status} />
            <button className="modal-close-btn" onClick={onClose} aria-label="Close modal">
              ✕
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* Metadata Grid */}
          <div className="modal-meta-grid">
            <div className="meta-item">
              <span className="meta-label">Uploaded At</span>
              <span className="meta-value">{formatDate(createdAt)}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Processed At</span>
              <span className="meta-value">{formatDate(processedAt)}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Match Score</span>
              <span className="meta-value font-bold text-accent">
                {matchPercentage !== undefined ? `${matchPercentage}%` : 'Not matched yet'}
              </span>
            </div>
          </div>

          {/* Error notice if failed */}
          {status === 'FAILED' && errorMessage && (
            <div className="modal-alert alert-error">
              <span className="alert-icon">⚠️</span>
              <div>
                <strong>Processing Error</strong>
                <p>{errorMessage}</p>
              </div>
            </div>
          )}

          {/* Match Skills Breakdown */}
          {matchResult && (
            <div className="modal-skills-section">
              <h3 className="section-heading">Skill Evaluation</h3>
              {matchResult.matchedSkills && matchResult.matchedSkills.length > 0 && (
                <div className="skills-block">
                  <span className="skills-block-title text-success">
                    ✓ Matched Skills ({matchResult.matchedSkills.length})
                  </span>
                  <div className="skills-pill-wrap">
                    {matchResult.matchedSkills.map((skill) => (
                      <span key={skill} className="skill-chip chip-matched">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {matchResult.missingSkills && matchResult.missingSkills.length > 0 && (
                <div className="skills-block">
                  <span className="skills-block-title text-warning">
                    ✕ Missing Skills ({matchResult.missingSkills.length})
                  </span>
                  <div className="skills-pill-wrap">
                    {matchResult.missingSkills.map((skill) => (
                      <span key={skill} className="skill-chip chip-missing">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Extracted Resume Text Viewer */}
          <div className="modal-resume-section">
            <div className="resume-viewer-header">
              <h3 className="section-heading">Extracted Resume Text</h3>
              {resumeText && (
                <button
                  type="button"
                  className="btn-copy"
                  onClick={handleCopyText}
                >
                  {copied ? '✓ Copied!' : '📋 Copy Text'}
                </button>
              )}
            </div>
            <div className="resume-viewer-box">
              {resumeText ? (
                <pre className="resume-pre">{resumeText}</pre>
              ) : (
                <p className="resume-empty">
                  {status === 'PROCESSING' || status === 'UPLOADING'
                    ? 'Resume text is currently being extracted by AWS pipeline...'
                    : 'No resume text available for this candidate.'}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
