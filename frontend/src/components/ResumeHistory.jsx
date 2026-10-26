import React from 'react';
import StatusBadge from './StatusBadge.jsx';

/**
 * ResumeHistory Component
 * Displays a dedicated history table of all uploaded resume documents,
 * their current pipeline status, timestamps, and quick inspection actions.
 */
export default function ResumeHistory({ candidates = [], onSelectCandidate }) {
  const formatDate = (isoStr) => {
    if (!isoStr) return '—';
    try {
      const d = new Date(isoStr);
      return d.toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short',
      });
    } catch (_) {
      return isoStr;
    }
  };

  if (!candidates || candidates.length === 0) {
    return (
      <div className="resume-history-empty">
        <p className="text-muted text-sm">No resume files uploaded yet.</p>
      </div>
    );
  }

  return (
    <div className="resume-history-container">
      <div className="history-table-wrapper">
        <table className="history-table">
          <thead>
            <tr>
              <th>Document</th>
              <th>Candidate Name</th>
              <th>Uploaded Date</th>
              <th>Processing Status</th>
              <th className="th-action">Action</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map((cand) => {
              const displayName = cand.candidateName || '—';
              const isReady = (cand.status || '').toUpperCase() === 'COMPLETED';

              return (
                <tr key={cand.candidateId} className="history-row">
                  <td className="history-doc-cell">
                    <span className="history-file-icon">📄</span>
                    <span className="history-filename" title={cand.filename}>
                      {cand.filename || 'resume.pdf'}
                    </span>
                  </td>
                  <td className="history-name-cell">Profile: {displayName}</td>
                  <td className="history-date-cell">{formatDate(cand.createdAt)}</td>
                  <td className="history-status-cell">
                    <StatusBadge status={cand.status} />
                  </td>
                  <td className="history-action-cell">
                    <button
                      type="button"
                      className="btn-history-inspect"
                      onClick={() => onSelectCandidate && onSelectCandidate(cand)}
                      title="Inspect extracted resume text"
                    >
                      {isReady ? 'View Text' : 'Details'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
