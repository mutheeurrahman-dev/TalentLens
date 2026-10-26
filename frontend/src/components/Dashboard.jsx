import React from 'react';
import TalentLensLogo from './TalentLensLogo.jsx';

/**
 * Dashboard Component
 * Clean presentation layout providing the fixed enterprise sidebar
 * (branding, AWS infrastructure health, section navigation, and configurations)
 * and the primary main content view.
 */
export default function Dashboard({
  headerRight,
  sidebarContent,
  mainContent,
  activeSection = 'overview',
  onSectionChange,
  candidateCount = 0,
}) {
  const NAV_ITEMS = [
    { id: 'overview', label: 'Dashboard Overview', icon: '📊' },
    { id: 'candidates', label: 'Candidate Pool', icon: '👥', badge: candidateCount },
    { id: 'requirements', label: 'Job Criteria', icon: '🎯' },
    { id: 'upload', label: 'Upload Portal', icon: '📄' },
  ];

  return (
    <div className="dashboard-container">
      {/* Fixed Professional Sidebar */}
      <aside className="app-sidebar">
        {/* Brand Header with New TalentLens Logo */}
        <div className="sidebar-brand">
          <TalentLensLogo size={42} showWordmark={true} />
        </div>

        {/* AWS Infrastructure Live Status Pill */}
        <div className="aws-status-widget">
          <div className="status-live-indicator">
            <span className="live-dot" />
            <span className="live-text">AWS ap-south-1</span>
          </div>
          <span className="status-chip">Online</span>
        </div>

        {/* Section Navigation Menu */}
        {onSectionChange && (
          <nav className="sidebar-nav-menu">
            <span className="nav-section-title">Sections</span>
            {NAV_ITEMS.map((item) => (
              <button
                key={item.id}
                type="button"
                className={`sidebar-nav-item ${activeSection === item.id ? 'active' : ''}`}
                onClick={() => onSectionChange(item.id)}
              >
                <span className="nav-item-icon">{item.icon}</span>
                <span className="nav-item-label">{item.label}</span>
                {item.badge !== undefined && item.badge > 0 && (
                  <span className="nav-item-badge">{item.badge}</span>
                )}
              </button>
            ))}
          </nav>
        )}

        {/* Sidebar Scrollable Widgets (Upload and/or Matching Controls) */}
        <div className="sidebar-scrollable-content">
          {sidebarContent}
        </div>

        {/* Sidebar Footer */}
        <div className="sidebar-footer">
          <span className="footer-meta">TalentLens Cloud v1.2</span>
          <span className="footer-sub">AWS Lambda • SQS • DynamoDB • S3</span>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="app-main">
        {headerRight && <div className="main-header-bar">{headerRight}</div>}
        <div className="main-content-inner">
          {mainContent}
        </div>
      </main>
    </div>
  );
}
