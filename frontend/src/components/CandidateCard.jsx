import React from 'react';
import StatusBadge from './StatusBadge.jsx';

/**
 * CandidateCard Component
 * Displays a candidate summary card with match score, progress bar,
 * matched/missing skills badges, and an action to inspect the profile.
 */
export default function CandidateCard({ candidate, rank, onSelect }) {
  if (!candidate) return null;

  const {
    candidateId,
    filename,
    candidateName,
    status = 'PROCESSING',
    createdAt,
    matchResult,
    errorMessage,
  } = candidate;

  const displayName = candidateName || filename || `Candidate #${candidateId?.slice(0, 8) || 'N/A'}`;
  const isProcessing = status?.toUpperCase() === 'PROCESSING' || status?.toUpperCase() === 'UPLOADING';
  const isFailed = status?.toUpperCase() === 'FAILED';

  // Determine match percentage
  const matchPercentage = matchResult?.matchPercentage ?? null;
  let barGradientClass = 'gradient-low';
  if (matchPercentage !== null) {
    if (matchPercentage >= 70) {
      barGradientClass = 'gradient-high';
    } else if (matchPercentage >= 40) {
      barGradientClass = 'gradient-medium';
    }
  }

  // Format date
  const formatDate = (isoStr) => {
    if (!isoStr) return '';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    } catch (_) {
      return '';
    }
  };

  const initials = displayName
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0])
    .join('')
    .toUpperCase() || 'C';

  return (
    <div
      className="card candidate-card"
      data-testid={`candidate-card-${candidateId}`}
      onClick={() => onSelect && onSelect(candidate)}
    >
      {/* Top Bar with Avatar, Name, and Status */}
      <div className="candidate-header">
        <div className="candidate-identity">
          <div className="candidate-avatar">
            {rank && <span className="rank-indicator">#{rank}</span>}
            <span className="avatar-initials">{initials}</span>
          </div>
          <div className="candidate-title-info">
            <h3 className="candidate-name" title={displayName}>
              {displayName}
            </h3>
            <div className="candidate-submeta">
              {filename && <span className="candidate-filename">📄 {filename}</span>}
              {createdAt && <span className="candidate-date">• {formatDate(createdAt)}</span>}
            </div>
          </div>
        </div>
        <StatusBadge status={status} />
      </div>

      {/* Processing State */}
      {isProcessing && (
        <div className="candidate-processing-state">
          <div className="loading-spinner small"></div>
          <span>Parsing resume with AWS pipeline...</span>
        </div>
      )}

      {/* Failed State */}
      {isFailed && (
        <div className="candidate-failed-state">
          <span>⚠️ {errorMessage || 'Failed to process resume document.'}</span>
        </div>
      )}

      {/* Unranked / Completed State */}
      {!matchResult && !isProcessing && !isFailed && (
        <div className="candidate-unranked-box">
          <div className="unranked-header">
            <span className="unranked-status-text">⚡ Ready for Screening</span>
          </div>
          <p className="unranked-subtext">
            Resume parsed. Select Job Requirements to evaluate skills and calculate ranking.
          </p>
        </div>
      )}

      {/* Match Section */}
      {matchResult && (
        <div className="candidate-match-section">
          <div className="match-score-row">
            <span className="match-label">Match Score</span>
            <span className="match-percentage font-bold">{matchPercentage}%</span>
          </div>

          <div className="match-bar-track">
            <div
              className={`match-bar-fill ${barGradientClass}`}
              style={{ width: `${Math.min(100, Math.max(0, matchPercentage))}%` }}
            />
          </div>

          {matchResult.matchedSkills && matchResult.matchedSkills.length > 0 ? (
            <div className="skills-group">
              <span className="skills-group-title">Matched Skills:</span>
              <div className="skills-pill-container">
                {matchResult.matchedSkills.slice(0, 5).map((skill) => (
                  <span key={skill} className="skill-tag skill-matched">
                    ✓ {skill}
                  </span>
                ))}
                {matchResult.matchedSkills.length > 5 && (
                  <span className="skill-tag skill-more">
                    +{matchResult.matchedSkills.length - 5} more
                  </span>
                )}
              </div>
            </div>
          ) : (
            <div className="skills-group">
              <span className="skills-group-title">Matched Skills:</span>
              <span className="skill-tag skill-zero">0 skills matched</span>
            </div>
          )}

          {matchResult.missingSkills && matchResult.missingSkills.length > 0 && (
            <div className="skills-group">
              <span className="skills-group-title">Missing Skills:</span>
              <div className="skills-pill-container">
                {matchResult.missingSkills.slice(0, 4).map((skill) => (
                  <span key={skill} className="skill-tag skill-missing">
                    ✕ {skill}
                  </span>
                ))}
                {matchResult.missingSkills.length > 4 && (
                  <span className="skill-tag skill-more">
                    +{matchResult.missingSkills.length - 4} more
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Card Action Footer */}
      <div className="candidate-card-footer">
        <button
          type="button"
          className="btn-card-action"
          onClick={(e) => {
            e.stopPropagation();
            if (onSelect) onSelect(candidate);
          }}
        >
          View Details →
        </button>
      </div>
    </div>
  );
}
