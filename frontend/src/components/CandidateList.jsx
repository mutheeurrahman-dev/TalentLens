import React, { useState, useMemo } from 'react';
import CandidateCard from './CandidateCard.jsx';
import CandidateTable from './CandidateTable.jsx';
import CandidateDetailModal from './CandidateDetailModal.jsx';
import SummaryCards from './SummaryCards.jsx';

/**
 * CandidateList Component
 * Central place to browse, evaluate, and dynamically rank candidate resumes.
 * Distinguishes between the raw Candidate Pool and active job-specific Rankings.
 */
export default function CandidateList({
  candidates = [],
  loading = false,
  onRefresh,
  activeJobMatch = null,
  onClearMatch,
  onNavigate,
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState(activeJobMatch ? 'MATCH_DESC' : 'DATE_DESC');
  const [viewMode, setViewMode] = useState('GRID'); // 'GRID' | 'TABLE'
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  // Filter and sort candidates
  const processedCandidates = useMemo(() => {
    let list = [...candidates];

    // Filter by status
    if (statusFilter !== 'ALL') {
      list = list.filter((c) => {
        const s = (c.status || '').toUpperCase();
        if (statusFilter === 'PIPELINE') return s === 'PROCESSING' || s === 'UPLOADING';
        return s === statusFilter;
      });
    }

    // Filter by search query (name, filename, or matched skills)
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      list = list.filter((c) => {
        const name = (c.candidateName || '').toLowerCase();
        const file = (c.filename || '').toLowerCase();
        const skills = (c.matchResult?.matchedSkills || []).map((s) => s.toLowerCase());
        const hasSkill = skills.some((s) => s.includes(q));
        return name.includes(q) || file.includes(q) || hasSkill;
      });
    }

    // Sorting
    list.sort((a, b) => {
      if (sortBy === 'MATCH_DESC') {
        const aPercent = a.matchResult?.matchPercentage;
        const bPercent = b.matchResult?.matchPercentage;
        if (aPercent !== undefined && bPercent !== undefined) return bPercent - aPercent;
        if (aPercent !== undefined) return -1;
        if (bPercent !== undefined) return 1;
        return new Date(b.createdAt || 0) - new Date(a.createdAt || 0);
      }
      if (sortBy === 'MATCH_ASC') {
        const aPercent = a.matchResult?.matchPercentage;
        const bPercent = b.matchResult?.matchPercentage;
        if (aPercent !== undefined && bPercent !== undefined) return aPercent - bPercent;
        if (aPercent !== undefined) return 1;
        if (bPercent !== undefined) return -1;
        return new Date(b.createdAt || 0) - new Date(a.createdAt || 0);
      }
      if (sortBy === 'DATE_DESC') {
        return new Date(b.createdAt || 0) - new Date(a.createdAt || 0);
      }
      if (sortBy === 'DATE_ASC') {
        return new Date(a.createdAt || 0) - new Date(b.createdAt || 0);
      }
      if (sortBy === 'NAME_ASC') {
        const aName = a.candidateName || a.filename || '';
        const bName = b.candidateName || b.filename || '';
        return aName.localeCompare(bName);
      }
      return 0;
    });

    return list;
  }, [candidates, statusFilter, searchQuery, sortBy]);

  // Loading spinner during initial fetch
  if (loading && candidates.length === 0) {
    return (
      <div className="candidate-list-empty-state card">
        <div className="loading-spinner"></div>
        <p className="loading-text">Loading candidates...</p>
      </div>
    );
  }

  // Entire pool is empty
  if (!candidates || candidates.length === 0) {
    return (
      <div className="card empty-state">
        <div className="empty-state-icon">📋</div>
        <h3>No candidates yet</h3>
        <p>Upload candidate resumes to get started with screening and skill matching.</p>
        {onNavigate && (
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => onNavigate('upload')}
          >
            Upload Resume
          </button>
        )}
      </div>
    );
  }

  const completedEligibleCount = candidates.filter(
    (c) => (c.status || '').toUpperCase() === 'COMPLETED'
  ).length;

  return (
    <div className="candidate-dashboard-wrap">
      {/* 1. Summary Metric Stat Cards */}
      <SummaryCards candidates={candidates} />

      {/* 2. Active Match Criteria Banner OR Unranked Pool Notice */}
      {activeJobMatch ? (
        <div className="active-criteria-banner card">
          <div className="criteria-header-row">
            <div className="criteria-title-group">
              <span className="criteria-badge">🎯 Active Job Ranking</span>
              <h2 className="criteria-job-title">
                {activeJobMatch.jobTitle || 'Custom Role Match'}
              </h2>
            </div>
            <div className="criteria-actions-group">
              {onNavigate && (
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => onNavigate('requirements')}
                >
                  Change Criteria
                </button>
              )}
              {onClearMatch && (
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={onClearMatch}
                  title="Clear active match rankings and view unranked pool"
                >
                  Reset Rankings
                </button>
              )}
            </div>
          </div>

          <div className="criteria-details-row">
            <span className="criteria-label">Evaluated Requirements:</span>
            <span className="criteria-text">{activeJobMatch.requirements}</span>
          </div>

          <div className="criteria-meta-row">
            <span>
              Dynamic evaluation calculated at {new Date(activeJobMatch.matchedAt).toLocaleTimeString()}
            </span>
            <span>•</span>
            <span className="text-success font-semibold">
              {completedEligibleCount} eligible candidate{completedEligibleCount === 1 ? '' : 's'} ranked
            </span>
          </div>
        </div>
      ) : (
        <div className="pool-info-banner card">
          <div className="pool-info-left">
            <span className="pool-info-icon">ℹ️</span>
            <div>
              <h3 className="pool-info-title">Candidate Pool (Unranked)</h3>
              <p className="pool-info-desc">
                Browsing all uploaded resumes in database. Only successfully processed candidates are eligible for skill matching. Enter job requirements to generate dynamic rankings.
              </p>
            </div>
          </div>
          {onNavigate && (
            <button
              type="button"
              className="btn btn-primary btn-sm pool-action-btn"
              onClick={() => onNavigate('requirements')}
            >
              Match Candidates ({completedEligibleCount}) →
            </button>
          )}
        </div>
      )}

      {/* 3. Candidate Section Header & Controls */}
      <div className="candidate-list-header-card card">
        <div className="list-title-row">
          <div className="list-title-group">
            <h2 className="list-title">Candidates ({candidates.length})</h2>
            <span className="list-subtitle">
              {activeJobMatch
                ? `Ranked for ${activeJobMatch.jobTitle || 'specified job criteria'}`
                : processedCandidates.length === candidates.length
                ? 'Showing all candidates in database'
                : `Showing ${processedCandidates.length} filtered candidate${processedCandidates.length === 1 ? '' : 's'}`}
            </span>
          </div>

          {/* View Mode Toggle and Refresh Button */}
          <div className="list-actions-right">
            {onRefresh && (
              <button
                type="button"
                className="btn-icon"
                onClick={onRefresh}
                title="Refresh candidate data"
              >
                🔄
              </button>
            )}
            <div className="view-toggle-wrap">
              <button
                type="button"
                className={`toggle-btn ${viewMode === 'GRID' ? 'active' : ''}`}
                onClick={() => setViewMode('GRID')}
                title="Cards view"
              >
                Grid
              </button>
              <button
                type="button"
                className={`toggle-btn ${viewMode === 'TABLE' ? 'active' : ''}`}
                onClick={() => setViewMode('TABLE')}
                title="Table view"
              >
                Table
              </button>
            </div>
          </div>
        </div>

        {/* Search, Status Filter & Sorting Bar */}
        <div className="filters-toolbar">
          {/* Live Search Input */}
          <div className="search-input-box">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              className="search-field"
              placeholder="Search by name, file, or skill (e.g. Python, React)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                type="button"
                className="search-clear-btn"
                onClick={() => setSearchQuery('')}
              >
                ✕
              </button>
            )}
          </div>

          {/* Status Filter Tabs */}
          <div className="status-tabs-wrap">
            <button
              type="button"
              className={`status-tab ${statusFilter === 'ALL' ? 'active' : ''}`}
              onClick={() => setStatusFilter('ALL')}
            >
              All ({candidates.length})
            </button>
            <button
              type="button"
              className={`status-tab ${statusFilter === 'COMPLETED' ? 'active' : ''}`}
              onClick={() => setStatusFilter('COMPLETED')}
            >
              Completed ({candidates.filter((c) => (c.status || '').toUpperCase() === 'COMPLETED').length})
            </button>
            <button
              type="button"
              className={`status-tab ${statusFilter === 'PIPELINE' ? 'active' : ''}`}
              onClick={() => setStatusFilter('PIPELINE')}
            >
              Pipeline ({candidates.filter((c) => {
                const s = (c.status || '').toUpperCase();
                return s === 'PROCESSING' || s === 'UPLOADING';
              }).length})
            </button>
            <button
              type="button"
              className={`status-tab ${statusFilter === 'FAILED' ? 'active' : ''}`}
              onClick={() => setStatusFilter('FAILED')}
            >
              Failed ({candidates.filter((c) => (c.status || '').toUpperCase() === 'FAILED').length})
            </button>
          </div>

          {/* Sort Dropdown */}
          <div className="sort-box">
            <label htmlFor="sort-select" className="sort-label">Sort:</label>
            <select
              id="sort-select"
              className="sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="MATCH_DESC">Match Score (High → Low)</option>
              <option value="MATCH_ASC">Match Score (Low → High)</option>
              <option value="DATE_DESC">Newest Uploaded</option>
              <option value="DATE_ASC">Oldest Uploaded</option>
              <option value="NAME_ASC">Name (A → Z)</option>
            </select>
          </div>
        </div>
      </div>

      {/* 4. Candidate Views (Cards vs Table) */}
      {processedCandidates.length === 0 ? (
        <div className="card empty-filtered-state">
          <div className="empty-state-icon">🔍</div>
          <h3>No matching candidates</h3>
          <p>Try adjusting your search query or status filter.</p>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => {
              setSearchQuery('');
              setStatusFilter('ALL');
            }}
          >
            Reset Filters
          </button>
        </div>
      ) : viewMode === 'GRID' ? (
        <div className="candidate-list-grid">
          {processedCandidates.map((candidate, idx) => {
            const hasMatch = activeJobMatch && candidate.matchResult && typeof candidate.matchResult.matchPercentage === 'number';
            return (
              <CandidateCard
                key={candidate.candidateId || candidate.filename || idx}
                candidate={candidate}
                rank={hasMatch ? idx + 1 : undefined}
                onSelect={setSelectedCandidate}
              />
            );
          })}
        </div>
      ) : (
        <CandidateTable
          candidates={processedCandidates}
          activeJobMatch={activeJobMatch}
          onSelect={setSelectedCandidate}
        />
      )}

      {/* 5. Candidate Details Modal Dialog */}
      {selectedCandidate && (
        <CandidateDetailModal
          candidate={selectedCandidate}
          onClose={() => setSelectedCandidate(null)}
        />
      )}
    </div>
  );
}
