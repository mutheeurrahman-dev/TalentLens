import React, { useState, useEffect, useRef, useCallback } from 'react';
import Dashboard from './components/Dashboard.jsx';
import DashboardOverview from './components/DashboardOverview.jsx';
import ResumeUploader from './components/ResumeUploader.jsx';
import JobRequirements from './components/JobRequirements.jsx';
import CandidateList from './components/CandidateList.jsx';
import CandidateDetailModal from './components/CandidateDetailModal.jsx';
import { getCandidates, matchCandidates } from './api/api.js';

export default function App() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [matching, setMatching] = useState(false);
  const [error, setError] = useState(null);
  const [activeJobMatch, setActiveJobMatch] = useState(null);
  const [activeSection, setActiveSection] = useState('overview'); // 'overview' | 'candidates' | 'requirements' | 'upload'
  const [inspectCandidate, setInspectCandidate] = useState(null);

  const pollingRef = useRef(null);

  // Fetch candidate list from API
  const fetchCandidates = useCallback(async () => {
    try {
      const data = await getCandidates();
      setCandidates((prevList) => {
        // Preserve matchResult if previously computed for current active job match
        const matchMap = new Map();
        prevList.forEach((c) => {
          if (c.matchResult) matchMap.set(c.candidateId, c.matchResult);
        });

        return data.map((cand) => {
          if (matchMap.has(cand.candidateId)) {
            return { ...cand, matchResult: matchMap.get(cand.candidateId) };
          }
          return cand;
        });
      });
      setError(null);
    } catch (err) {
      console.error('Error fetching candidates:', err);
      setError(err.message || 'Failed to load candidates.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchCandidates();
  }, [fetchCandidates]);

  // Polling logic: poll every 5s while any candidate has status UPLOADING or PROCESSING
  useEffect(() => {
    const hasActiveTasks = candidates.some((c) => {
      const status = (c.status || '').toUpperCase();
      return status === 'UPLOADING' || status === 'PROCESSING';
    });

    if (hasActiveTasks) {
      if (!pollingRef.current) {
        pollingRef.current = setInterval(() => {
          fetchCandidates();
        }, 5000);
      }
    } else {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    }

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, [candidates, fetchCandidates]);

  // Handle successful upload of a resume
  const handleUploadComplete = (candidateId, filename) => {
    // Optimistically add or update candidate in list
    setCandidates((prev) => [
      {
        candidateId,
        filename,
        candidateName: filename.replace(/\.[^/.]+$/, ''),
        status: 'PROCESSING',
      },
      ...prev.filter((c) => c.candidateId !== candidateId),
    ]);

    // Trigger immediate refresh from server
    fetchCandidates();
  };

  // Handle matching candidates against job requirements
  const handleMatch = async (title, reqs) => {
    setMatching(true);
    setError(null);

    try {
      // Only successfully processed candidates are eligible for skill matching
      const eligibleCandidates = candidates.filter(
        (c) => (c.status || '').toUpperCase() === 'COMPLETED'
      );
      const eligibleIds = eligibleCandidates.map((c) => c.candidateId).filter(Boolean);

      const matchedData = await matchCandidates(title, reqs, eligibleIds);

      // Create a map of updated candidate information from match results
      const resultMap = new Map();
      matchedData.forEach((item) => {
        resultMap.set(item.candidateId, item);
      });

      // Freshly assign scores: completed candidates receive their matchResult;
      // non-completed remain undefined.
      setCandidates((prev) =>
        prev.map((c) => {
          const isCompleted = (c.status || '').toUpperCase() === 'COMPLETED';
          if (!isCompleted) {
            return { ...c, matchResult: undefined };
          }
          if (resultMap.has(c.candidateId)) {
            const updated = resultMap.get(c.candidateId);
            return {
              ...c,
              ...updated,
              matchResult: updated.matchResult || {
                matchPercentage: updated.matchPercentage ?? 0,
                matchedSkills: updated.matchedSkills || [],
                missingSkills: updated.missingSkills || [],
              },
            };
          }
          return {
            ...c,
            matchResult: {
              matchPercentage: 0,
              matchedSkills: [],
              missingSkills: [],
            },
          };
        })
      );

      // Record active criteria
      setActiveJobMatch({
        jobTitle: title,
        requirements: reqs,
        matchedAt: new Date().toISOString(),
      });

      // Automatically navigate to candidate rankings view
      setActiveSection('candidates');
    } catch (err) {
      console.error('Match failed:', err);
      setError(err.message || 'Failed to match candidates against requirements.');
    } finally {
      setMatching(false);
    }
  };

  // Reset active job matching back to raw candidate pool
  const handleClearMatch = () => {
    setActiveJobMatch(null);
    setCandidates((prev) => prev.map((c) => ({ ...c, matchResult: undefined })));
  };

  const completedCount = candidates.filter(
    (c) => (c.status || '').toUpperCase() === 'COMPLETED'
  ).length;

  return (
    <div className="app">
      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button
            type="button"
            className="error-dismiss-btn"
            onClick={() => setError(null)}
          >
            ✕
          </button>
        </div>
      )}

      <Dashboard
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        candidateCount={candidates.length}
        sidebarContent={
          <div className="sidebar-quick-stats card">
            <h3 className="quick-stats-title">Pipeline Summary</h3>
            <div className="quick-stat-row">
              <span className="quick-stat-label">Total Resumes:</span>
              <span className="quick-stat-val">{candidates.length}</span>
            </div>
            <div className="quick-stat-row">
              <span className="quick-stat-label">Ready for Match:</span>
              <span className="quick-stat-val text-success">{completedCount}</span>
            </div>
            <div className="quick-stat-row">
              <span className="quick-stat-label">AWS Pipeline:</span>
              <span className="quick-stat-val text-accent">Active</span>
            </div>
          </div>
        }
        mainContent={
          <div className="main-sections-container">
            {/* Top View Mode Switcher Tabs */}
            <div className="main-section-tabs">
              <button
                type="button"
                data-testid="tab-overview"
                className={`section-tab-btn ${activeSection === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveSection('overview')}
              >
                📊 Dashboard Overview
              </button>
              <button
                type="button"
                data-testid="tab-candidates"
                className={`section-tab-btn ${activeSection === 'candidates' ? 'active' : ''}`}
                onClick={() => setActiveSection('candidates')}
              >
                👥 Candidate Pool {activeJobMatch ? '— Ranked' : ''} ({candidates.length})
              </button>
              <button
                type="button"
                data-testid="tab-requirements"
                className={`section-tab-btn ${activeSection === 'requirements' ? 'active' : ''}`}
                onClick={() => setActiveSection('requirements')}
              >
                🎯 Job Requirements
              </button>
              <button
                type="button"
                data-testid="tab-upload"
                className={`section-tab-btn ${activeSection === 'upload' ? 'active' : ''}`}
                onClick={() => setActiveSection('upload')}
              >
                📄 Resume Upload
              </button>
            </div>

            {/* View 1: Clean Dashboard Overview (No Upload form, No Job textarea form) */}
            {activeSection === 'overview' && (
              <DashboardOverview
                candidates={candidates}
                activeJobMatch={activeJobMatch}
                onNavigate={setActiveSection}
                onSelectCandidate={setInspectCandidate}
              />
            )}

            {/* View 2: Candidate Pool & Ranked Results */}
            {activeSection === 'candidates' && (
              <section id="section-results" className="app-section">
                <CandidateList
                  candidates={candidates}
                  loading={loading}
                  onRefresh={fetchCandidates}
                  activeJobMatch={activeJobMatch}
                  onClearMatch={handleClearMatch}
                  onNavigate={setActiveSection}
                />
              </section>
            )}

            {/* View 3: Dedicated Job Requirements Form */}
            {activeSection === 'requirements' && (
              <section id="section-requirements" className="app-section">
                <JobRequirements
                  onMatch={handleMatch}
                  loading={matching}
                  candidateCount={completedCount}
                  activeJobMatch={activeJobMatch}
                />
              </section>
            )}

            {/* View 4: Dedicated Resume Upload & Ingestion History */}
            {activeSection === 'upload' && (
              <section id="section-upload" className="app-section">
                <ResumeUploader
                  onUploadComplete={handleUploadComplete}
                  candidates={candidates}
                  onSelectCandidate={setInspectCandidate}
                />
              </section>
            )}

            {/* Inspect Candidate Details Modal */}
            {inspectCandidate && (
              <CandidateDetailModal
                candidate={inspectCandidate}
                onClose={() => setInspectCandidate(null)}
              />
            )}
          </div>
        }
      />
    </div>
  );
}
