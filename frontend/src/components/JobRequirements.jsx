import React, { useState, useEffect } from 'react';

/**
 * JobRequirements Component
 * Form allowing recruiters to enter job specifications or click quick presets
 * to trigger automatic skill ranking across all eligible candidates.
 */
export default function JobRequirements({
  onMatch,
  loading = false,
  candidateCount = 0,
  activeJobMatch = null,
}) {
  const [jobTitle, setJobTitle] = useState(activeJobMatch?.jobTitle || '');
  const [requirements, setRequirements] = useState(activeJobMatch?.requirements || '');

  // Keep state synced when activeJobMatch changes externally
  useEffect(() => {
    if (activeJobMatch) {
      setJobTitle(activeJobMatch.jobTitle || '');
      setRequirements(activeJobMatch.requirements || '');
    }
  }, [activeJobMatch]);

  const PRESETS = [
    {
      title: 'Junior Full Stack Developer',
      skills: 'React, JavaScript, Node.js, SQL, HTML, CSS, Git',
    },
    {
      title: 'Cloud / DevOps Engineer',
      skills: 'AWS, Docker, Kubernetes, Linux, Terraform, CI/CD, Python',
    },
    {
      title: 'Python Developer',
      skills: 'Python, SQL, APIs, FastAPI, Docker, PostgreSQL, Pandas',
    },
  ];

  const applyPreset = (preset) => {
    setJobTitle(preset.title);
    setRequirements(preset.skills);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!requirements.trim() || loading || candidateCount === 0) return;
    if (onMatch) {
      onMatch(jobTitle.trim(), requirements.trim());
    }
  };

  const isCriteriaModified = activeJobMatch && (
    jobTitle.trim() !== (activeJobMatch.jobTitle || '').trim() ||
    requirements.trim() !== (activeJobMatch.requirements || '').trim()
  );

  const isButtonDisabled = loading || candidateCount === 0 || !requirements.trim();

  return (
    <div className="card job-form-section">
      <div className="section-header-wrap">
        <span className="section-badge badge-accent">AI Skill Matcher</span>
        <h2 className="section-title">Job Requirements</h2>
        <p className="section-subtitle">
          Define target qualifications to calculate dynamic match scores for{' '}
          <strong>{candidateCount}</strong> completed candidate{candidateCount === 1 ? '' : 's'}.
        </p>
      </div>

      {/* Active Match Status or Modified Notice */}
      {isCriteriaModified && (
        <div className="alert-banner alert-warning">
          <span>⚠️ Requirements changed since last match. Click "Match Candidates" to recalculate fresh scores.</span>
        </div>
      )}

      {activeJobMatch && !isCriteriaModified && (
        <div className="alert-banner alert-success">
          <span>🎯 Active criteria: Currently ranked for "{activeJobMatch.jobTitle || 'Custom Role'}"</span>
        </div>
      )}

      {/* Quick Presets */}
      <div className="presets-container">
        <span className="presets-label">Quick Role Presets:</span>
        <div className="presets-buttons-wrap">
          {PRESETS.map((p) => (
            <button
              key={p.title}
              type="button"
              className="preset-pill"
              onClick={() => applyPreset(p)}
              disabled={loading}
            >
              {p.title}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="job-form">
        <div className="form-group">
          <label htmlFor="job-title" className="form-label">
            Job Title (Optional)
          </label>
          <input
            id="job-title"
            type="text"
            className="form-input"
            placeholder="e.g. Junior Full Stack Developer"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <div className="label-row">
            <label htmlFor="job-requirements" className="form-label">
              Skills / Job Description <span className="required-indicator">*</span>
            </label>
            <span className="char-count">{requirements.length} chars</span>
          </div>
          <textarea
            id="job-requirements"
            rows={5}
            className="form-textarea"
            placeholder="Paste required skills or full job description (e.g. React, JavaScript, Node.js, SQL)..."
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary btn-block match-btn"
          disabled={isButtonDisabled}
        >
          {loading ? (
            <span className="btn-loading-content">
              <span className="loading-spinner small"></span>
              <span>Evaluating Candidate Skills...</span>
            </span>
          ) : (
            `Match Candidates (${candidateCount})`
          )}
        </button>

        {candidateCount === 0 && (
          <p className="form-hint">Upload and process at least one resume before running matching.</p>
        )}
      </form>
    </div>
  );
}
