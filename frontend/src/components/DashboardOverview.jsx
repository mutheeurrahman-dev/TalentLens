import React from 'react';
import StatusBadge from './StatusBadge.jsx';
import SummaryCards from './SummaryCards.jsx';
import CloudArchitecture from './CloudArchitecture.jsx';

/**
 * DashboardOverview Component
 * Clean, executive-level overview focused strictly on key metrics, pipeline health,
 * active matching status, quick shortcuts, and recent candidate activity.
 * The heavy Upload and Job Requirements forms are kept in their dedicated sections.
 */
export default function DashboardOverview({
  candidates = [],
  activeJobMatch = null,
  onNavigate,
  onSelectCandidate,
}) {
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

  // Format date helper
  const formatDate = (isoStr) => {
    if (!isoStr) return '—';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    } catch (_) {
      return '—';
    }
  };

  // Get up to 5 most recent candidates
  const recentCandidates = [...candidates]
    .sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0))
    .slice(0, 5);

  // Identify highest match if active match criteria is present
  const topCandidate = activeJobMatch
    ? [...candidates]
        .filter((c) => c.matchResult && typeof c.matchResult.matchPercentage === 'number')
        .sort((a, b) => (b.matchResult?.matchPercentage || 0) - (a.matchResult?.matchPercentage || 0))[0]
    : null;

  return (
    <div className="dashboard-overview-container">
      {/* 1. Pipeline Summary KPI Metric Cards */}
      <SummaryCards candidates={candidates} />

      {/* 2. Cloud Architecture & Process Flow Section */}
      <CloudArchitecture />

      {/* 3. Active Screening & Matching Status Hero Banner */}
      <div className="overview-hero-card card">
        <div className="hero-status-row">
          <div className="hero-status-info">
            <span className="hero-badge">
              {activeJobMatch ? '🎯 Active Job Screening' : '⚡ AI Screening Pipeline'}
            </span>
            <h2 className="hero-heading">
              {activeJobMatch
                ? activeJobMatch.jobTitle || 'Custom Role Match'
                : 'Intelligent Resume Screening & Candidate Ranking'}
            </h2>
            <p className="hero-description">
              {activeJobMatch ? (
                <>
                  Rankings evaluated against requirements:{' '}
                  <strong className="text-accent">{activeJobMatch.requirements.slice(0, 100)}</strong>
                  {activeJobMatch.requirements.length > 100 ? '...' : ''}
                  {topCandidate && (
                    <span className="hero-top-match">
                      {' '}• Top Match:{' '}
                      <strong className="text-success">
                        {topCandidate.candidateName} ({topCandidate.matchResult.matchPercentage}%)
                      </strong>
                    </span>
                  )}
                </>
              ) : (
                `Currently managing ${total} candidate resume${total === 1 ? '' : 's'} (${completed} completed and ready for evaluation). Define job criteria to calculate dynamic match scores.`
              )}
            </p>
          </div>

          <div className="hero-cta-actions">
            {activeJobMatch ? (
              <button
                type="button"
                className="btn btn-primary hero-btn"
                onClick={() => onNavigate && onNavigate('candidates')}
              >
                View Candidate Results →
              </button>
            ) : (
              <button
                type="button"
                className="btn btn-primary hero-btn"
                onClick={() => onNavigate && onNavigate('requirements')}
                disabled={completed === 0}
              >
                Match Candidates →
              </button>
            )}
          </div>
        </div>

        {/* Quick Action Navigation Buttons */}
        <div className="overview-shortcuts-grid">
          <button
            type="button"
            className="shortcut-card"
            onClick={() => onNavigate && onNavigate('candidates')}
          >
            <div className="shortcut-icon-circle">👥</div>
            <div className="shortcut-text">
              <span className="shortcut-title">Candidate Pool</span>
              <span className="shortcut-sub">
                {candidates.length > 0
                  ? `Browse ${candidates.length} candidate${candidates.length === 1 ? '' : 's'}`
                  : 'View empty pool'}
              </span>
            </div>
          </button>

          <button
            type="button"
            className="shortcut-card"
            onClick={() => onNavigate && onNavigate('requirements')}
          >
            <div className="shortcut-icon-circle">🎯</div>
            <div className="shortcut-text">
              <span className="shortcut-title">Job Requirements</span>
              <span className="shortcut-sub">Set criteria & role presets</span>
            </div>
          </button>

          <button
            type="button"
            className="shortcut-card"
            onClick={() => onNavigate && onNavigate('upload')}
          >
            <div className="shortcut-icon-circle">📄</div>
            <div className="shortcut-text">
              <span className="shortcut-title">Upload Resume</span>
              <span className="shortcut-sub">Add PDF resumes to pool</span>
            </div>
          </button>
        </div>
      </div>

      {/* 3. Recent Activity & Processed Resumes Feed */}
      <div className="overview-recent-section card">
        <div className="overview-section-header">
          <div>
            <h3 className="overview-section-title">Candidates ({candidates.length})</h3>
            <span className="overview-section-sub">
              Recently ingested resumes & processing pipeline status
            </span>
          </div>

          {candidates.length > 0 && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => onNavigate && onNavigate('candidates')}
            >
              View Full Pool ({candidates.length}) →
            </button>
          )}
        </div>

        {candidates.length === 0 ? (
          <div className="card empty-state">
            <div className="empty-state-icon">📋</div>
            <h3>No candidates yet</h3>
            <p>Upload candidate resumes to get started with screening and skill matching.</p>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => onNavigate && onNavigate('upload')}
            >
              Upload New Resumes
            </button>
          </div>
        ) : (
          <div className="overview-candidates-table-wrap">
            <table className="overview-candidates-table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Filename</th>
                  <th>Upload Date</th>
                  <th>Status</th>
                  <th>Match Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {recentCandidates.map((cand) => {
                  const displayName = cand.candidateName || cand.filename || `Candidate #${cand.candidateId?.slice(0, 8)}`;
                  const initials = displayName
                    .split(' ')
                    .slice(0, 2)
                    .map((w) => w[0])
                    .join('')
                    .toUpperCase() || 'C';

                  const matchScore = cand.matchResult?.matchPercentage;

                  return (
                    <tr
                      key={cand.candidateId || cand.filename}
                      className="overview-table-row"
                      onClick={() => onSelectCandidate && onSelectCandidate(cand)}
                    >
                      <td>
                        <div className="overview-candidate-cell">
                          <div className="overview-avatar">{initials}</div>
                          <span className="overview-candidate-name">{displayName}</span>
                        </div>
                      </td>
                      <td>
                        <span className="overview-file-text">📄 {cand.filename}</span>
                      </td>
                      <td>
                        <span className="overview-date-text">{formatDate(cand.createdAt)}</span>
                      </td>
                      <td>
                        <StatusBadge status={cand.status} />
                      </td>
                      <td>
                        {matchScore !== undefined ? (
                          <div className="overview-score-chip">
                            <span className="score-num font-bold">{matchScore}%</span>
                            <span className="score-sub">matched</span>
                          </div>
                        ) : (
                          <span className="text-muted text-xs">
                            {(cand.status || '').toUpperCase() === 'COMPLETED'
                              ? 'Ready for match'
                              : 'In pipeline'}
                          </span>
                        )}
                      </td>
                      <td>
                        <button
                          type="button"
                          className="btn-inspect-mini"
                          onClick={(e) => {
                            e.stopPropagation();
                            if (onSelectCandidate) onSelectCandidate(cand);
                          }}
                        >
                          View →
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
