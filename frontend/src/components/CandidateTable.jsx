import React from 'react';
import StatusBadge from './StatusBadge.jsx';

/**
 * CandidateTable Component
 * High-density tabular layout for rapid screening of multiple candidates,
 * with ranking badges, match progress indicators, and row inspection actions.
 */
export default function CandidateTable({ candidates, activeJobMatch = null, onSelect }) {
  if (!candidates || candidates.length === 0) return null;

  const formatDate = (isoStr) => {
    if (!isoStr) return '—';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    } catch (_) {
      return '—';
    }
  };

  return (
    <div className="table-responsive-wrapper card">
      <table className="candidate-table">
        <thead>
          <tr>
            <th className="th-rank">#</th>
            <th className="th-name">Candidate</th>
            <th className="th-date">Upload Date</th>
            <th className="th-status">Status</th>
            <th className="th-score">Match Score</th>
            <th className="th-skills">Key Skills</th>
            <th className="th-actions">Actions</th>
          </tr>
        </thead>
        <tbody>
          {candidates.map((cand, idx) => {
            const displayName = cand.candidateName || cand.filename || `Candidate #${cand.candidateId?.slice(0, 8)}`;
            const isCompleted = (cand.status || '').toUpperCase() === 'COMPLETED';
            const hasMatch = activeJobMatch && cand.matchResult && typeof cand.matchResult.matchPercentage === 'number';
            const matchScore = hasMatch ? cand.matchResult.matchPercentage : undefined;
            const initials = displayName
              .split(' ')
              .slice(0, 2)
              .map((w) => w[0])
              .join('')
              .toUpperCase() || 'C';

            return (
              <tr
                key={cand.candidateId || cand.filename || idx}
                className="table-row"
                onClick={() => onSelect && onSelect(cand)}
              >
                <td className="td-rank">
                  <span className="rank-cell-pill">
                    {hasMatch ? `#${idx + 1}` : '—'}
                  </span>
                </td>
                <td className="td-name">
                  <div className="table-identity">
                    <div className="table-avatar">{initials}</div>
                    <div>
                      <div className="table-candidate-name">{displayName}</div>
                      <div className="table-candidate-filename">📄 {cand.filename}</div>
                    </div>
                  </div>
                </td>
                <td className="td-date">{formatDate(cand.createdAt)}</td>
                <td className="td-status">
                  <StatusBadge status={cand.status} />
                </td>
                <td className="td-score">
                  {hasMatch ? (
                    <div className="table-score-wrap">
                      <span className="table-score-val">{matchScore}%</span>
                      <div className="table-score-bar">
                        <div
                          className="table-score-fill"
                          style={{
                            width: `${Math.min(100, Math.max(0, matchScore))}%`,
                            background:
                              matchScore >= 70
                                ? 'linear-gradient(90deg, #10B981, #059669)'
                                : matchScore >= 40
                                ? 'linear-gradient(90deg, #6366F1, #8B5CF6)'
                                : 'linear-gradient(90deg, #F59E0B, #D97706)',
                          }}
                        />
                      </div>
                    </div>
                  ) : (
                    <span className="text-muted text-xs">
                      {isCompleted ? 'Ready for match' : '—'}
                    </span>
                  )}
                </td>
                <td className="td-skills">
                  {hasMatch ? (
                    cand.matchResult?.matchedSkills && cand.matchResult.matchedSkills.length > 0 ? (
                      <div className="table-skills-preview">
                        {cand.matchResult.matchedSkills.slice(0, 3).map((s) => (
                          <span key={s} className="table-skill-tag">
                            {s}
                          </span>
                        ))}
                        {cand.matchResult.matchedSkills.length > 3 && (
                          <span className="table-skill-more">
                            +{cand.matchResult.matchedSkills.length - 3}
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="text-muted text-xs">0 skills matched</span>
                    )
                  ) : (
                    <span className="text-muted text-xs">Not evaluated</span>
                  )}
                </td>
                <td className="td-actions">
                  <button
                    type="button"
                    className="table-view-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (onSelect) onSelect(cand);
                    }}
                  >
                    Inspect
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
