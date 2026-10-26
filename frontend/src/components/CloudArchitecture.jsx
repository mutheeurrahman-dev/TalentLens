import React, { useState } from 'react';

/**
 * CloudArchitecture Component
 * Compact, beginner-friendly cloud architecture diagram and process flow panel
 * reflecting the actual AWS Serverless Application Model (SAM) deployment in ap-south-1.
 * Suitable for technical review and college project demonstration.
 */
export default function CloudArchitecture() {
  const [isExpanded, setIsExpanded] = useState(true);

  const PROCESS_STEPS = [
    {
      step: '1',
      title: 'PDF Upload',
      service: 'Client Browser',
      icon: '📄',
      desc: 'User uploads resume PDF in browser via presigned PUT URL',
      badge: 'Frontend',
    },
    {
      step: '2',
      title: 'API Gateway',
      service: 'Amazon API Gateway',
      icon: '🚪',
      desc: 'Secure HTTP API routes client requests to backend handlers',
      badge: 'Entry Point',
    },
    {
      step: '3',
      title: 'Object Storage',
      service: 'Amazon S3',
      icon: '🪣',
      desc: 'Stores resume PDF securely and triggers ObjectCreated notification',
      badge: 'Storage',
    },
    {
      step: '4',
      title: 'Message Buffer',
      service: 'Amazon SQS',
      icon: '📬',
      desc: 'Decoupled queue buffers upload events with DLQ retry handling',
      badge: 'Queue',
    },
    {
      step: '5',
      title: 'Serverless Worker',
      service: 'AWS Lambda',
      icon: '⚡',
      desc: 'ProcessResume function automatically triggered by SQS batch',
      badge: 'Compute',
    },
    {
      step: '6',
      title: 'Text Extraction',
      service: 'pypdf Engine',
      icon: '🔍',
      desc: 'Extracts raw resume text & candidate name using lightweight parser',
      badge: 'Extraction',
    },
    {
      step: '7',
      title: 'Data Store',
      service: 'Amazon DynamoDB',
      icon: '🗄️',
      desc: 'Stores candidate metadata, extracted text, and pipeline status',
      badge: 'NoSQL DB',
    },
    {
      step: '8',
      title: 'Dynamic Ranking',
      service: 'Match Lambda',
      icon: '🎯',
      desc: 'Matches extracted text against job criteria to rank candidates',
      badge: 'Evaluation',
    },
  ];

  const AWS_SERVICES = [
    {
      name: 'Amazon API Gateway',
      type: 'HTTP REST API',
      icon: '🚪',
      color: '#06b6d4',
      desc: 'Acts as the front door for frontend requests (/api/upload, /api/candidates, /api/match) with CORS support.',
    },
    {
      name: 'Amazon Simple Storage Service (S3)',
      type: 'Object Storage',
      icon: '🪣',
      color: '#10b981',
      desc: 'Securely stores uploaded PDF resumes using direct presigned URLs and triggers downstream event notifications.',
    },
    {
      name: 'Amazon Simple Queue Service (SQS)',
      type: 'Message Queue & DLQ',
      icon: '📬',
      color: '#f59e0b',
      desc: 'Decouples resume ingestion from processing, ensuring high traffic does not drop resume parsing tasks.',
    },
    {
      name: 'AWS Lambda (Python 3.12)',
      type: 'Serverless Compute',
      icon: '⚡',
      color: '#8b5cf6',
      desc: 'Runs backend handlers on demand (Upload, ProcessResume, Candidates, Match) without managing virtual servers.',
    },
    {
      name: 'Text Extraction (pypdf Engine)',
      type: 'In-Memory PDF Parser',
      icon: '🔍',
      color: '#6366f1',
      desc: 'Configured parser directly reading PDF streams to extract candidate text and name heuristics reliably.',
    },
    {
      name: 'Amazon DynamoDB',
      type: 'Serverless NoSQL Database',
      icon: '🗄️',
      color: '#3b82f6',
      desc: 'High-speed key-value database storing candidate profiles, processing statuses (COMPLETED/FAILED), and resume text.',
    },
  ];

  return (
    <div className="card cloud-arch-card" data-testid="cloud-architecture-panel">
      {/* Panel Header */}
      <div className="arch-header-row">
        <div className="arch-title-group">
          <div className="arch-icon-bubble">☁️</div>
          <div>
            <div className="arch-title-badge-row">
              <h3 className="arch-title">Cloud Architecture & Process Flow</h3>
              <span className="arch-region-chip">AWS ap-south-1</span>
              <span className="arch-type-chip">Serverless SAM</span>
            </div>
            <p className="arch-subtitle">
              Event-driven pipeline architecture powering automated resume screening and candidate ranking
            </p>
          </div>
        </div>

        <button
          type="button"
          className="btn-arch-toggle"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-expanded={isExpanded}
        >
          {isExpanded ? 'Collapse ▲' : 'View Architecture ▼'}
        </button>
      </div>

      {isExpanded && (
        <div className="arch-content-body">
          {/* 1. Compact Process Flow Diagram */}
          <div className="flow-section-wrapper">
            <span className="flow-section-label">End-to-End Event-Driven Process Flow:</span>
            <div className="flow-steps-container">
              {PROCESS_STEPS.map((item, idx) => (
                <React.Fragment key={item.step}>
                  <div className="flow-step-card">
                    <div className="step-badge-row">
                      <span className="step-num-pill">{item.step}</span>
                      <span className="step-role-pill">{item.badge}</span>
                    </div>
                    <div className="step-icon-wrap">{item.icon}</div>
                    <h4 className="step-title">{item.title}</h4>
                    <span className="step-service">{item.service}</span>
                    <p className="step-desc">{item.desc}</p>
                  </div>
                  {idx < PROCESS_STEPS.length - 1 && (
                    <div className="flow-connector" aria-hidden="true">
                      <span className="flow-arrow-icon">→</span>
                    </div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* 2. Actual Deployed AWS Services Breakdown */}
          <div className="services-section-wrapper">
            <span className="services-section-label">Deployed AWS Services & Responsibilities:</span>
            <div className="services-grid">
              {AWS_SERVICES.map((srv) => (
                <div key={srv.name} className="service-item-card">
                  <div className="service-item-header">
                    <span className="service-icon" style={{ borderColor: srv.color }}>
                      {srv.icon}
                    </span>
                    <div>
                      <h4 className="service-name">{srv.name}</h4>
                      <span className="service-type">{srv.type}</span>
                    </div>
                  </div>
                  <p className="service-desc">{srv.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 3. Reviewer Demonstration Callout */}
          <div className="arch-demo-note">
            <span className="demo-note-icon">💡</span>
            <div className="demo-note-text">
              <strong>College Project Demonstration Highlight:</strong> This architecture implements an asynchronous,
              decoupled event pattern. Resume upload to Amazon S3 instantly returns a response, while SQS and Lambda process
              heavy text extraction in the background without blocking the UI. Dynamically evaluates candidate skill match % on demand.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
