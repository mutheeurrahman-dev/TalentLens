import React from 'react';

/**
 * StatusBadge Component
 * Premium dark SaaS status indicator with pulsating live indicators
 * and high-contrast color badges.
 */
export default function StatusBadge({ status }) {
  const normStatus = (status || 'PROCESSING').toUpperCase();

  let badgeClass = 'status-badge';
  let label = 'Processing';
  let showPulse = false;

  switch (normStatus) {
    case 'UPLOADING':
      badgeClass += ' status-uploading';
      label = 'Uploading';
      showPulse = true;
      break;
    case 'PROCESSING':
      badgeClass += ' status-processing';
      label = 'Analyzing';
      showPulse = true;
      break;
    case 'COMPLETED':
      badgeClass += ' status-completed';
      label = 'Completed';
      break;
    case 'FAILED':
      badgeClass += ' status-failed';
      label = 'Failed';
      break;
    default:
      badgeClass += ' status-processing';
      label = normStatus;
      break;
  }

  return (
    <span className={badgeClass}>
      <span className={`status-dot ${showPulse ? 'pulse' : ''}`} />
      <span className="status-label">{label}</span>
    </span>
  );
}
