import React from 'react';

/**
 * TalentLensLogo Component
 * Bespoke corporate SVG brand mark combining a structured resume document
 * with an optical precision lens, paired with a modern typography wordmark.
 *
 * @param {number} size - Pixel dimensions for the icon mark (default: 38)
 * @param {boolean} showWordmark - Whether to display the text logo (default: true)
 * @param {string} subtitle - Optional tagline beneath the brand wordmark
 * @param {string} className - Optional container CSS class
 */
export default function TalentLensLogo({
  size = 38,
  showWordmark = true,
  subtitle = 'AI Resume Screening & Ranking',
  className = '',
}) {
  return (
    <div className={`talentlens-brand-wrapper ${className}`}>
      {/* Precision SVG Brand Mark */}
      <svg
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="talentlens-logo-mark"
        aria-label="TalentLens Logo"
      >
        <defs>
          <linearGradient id="tlDocGrad" x1="8" y1="4" x2="28" y2="38" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#1E293B" />
            <stop offset="100%" stopColor="#0F172A" />
          </linearGradient>

          <linearGradient id="tlLensRingGrad" x1="18" y1="14" x2="38" y2="36" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#38BDF8" />
            <stop offset="50%" stopColor="#818CF8" />
            <stop offset="100%" stopColor="#C084FC" />
          </linearGradient>

          <radialGradient id="tlLensGlassGlow" cx="28" cy="25" r="12" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.4" />
            <stop offset="60%" stopColor="#6366F1" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#0B0F19" stopOpacity="0.85" />
          </radialGradient>

          <linearGradient id="tlHandleGrad" x1="35" y1="33" x2="44" y2="42" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#818CF8" />
            <stop offset="100%" stopColor="#4F46E5" />
          </linearGradient>
        </defs>

        {/* Document Silhouette */}
        <path
          d="M8 8C8 5.79086 9.79086 4 12 4H24L32 12V38C32 40.2091 30.2091 42 28 42H12C9.79086 42 8 40.2091 8 38V8Z"
          fill="url(#tlDocGrad)"
          stroke="rgba(99, 102, 241, 0.45)"
          strokeWidth="1.75"
        />

        {/* Document Folded Corner */}
        <path
          d="M24 4V10C24 11.1046 24.8954 12 26 12H32"
          stroke="rgba(99, 102, 241, 0.55)"
          strokeWidth="1.75"
          fill="#131D33"
        />

        {/* Resume Content Scan Lines */}
        <line x1="13" y1="14" x2="20" y2="14" stroke="#94A3B8" strokeWidth="1.75" strokeLinecap="round" opacity="0.65" />
        <line x1="13" y1="19" x2="22" y2="19" stroke="#94A3B8" strokeWidth="1.75" strokeLinecap="round" opacity="0.65" />
        <line x1="13" y1="24" x2="19" y2="24" stroke="#94A3B8" strokeWidth="1.75" strokeLinecap="round" opacity="0.65" />
        <line x1="13" y1="29" x2="17" y2="29" stroke="#94A3B8" strokeWidth="1.75" strokeLinecap="round" opacity="0.65" />

        {/* Optical Lens Body */}
        <circle
          cx="28"
          cy="25"
          r="11"
          fill="url(#tlLensGlassGlow)"
          stroke="url(#tlLensRingGrad)"
          strokeWidth="2.25"
        />

        {/* Focus Target / Iris Center */}
        <circle cx="28" cy="25" r="3" fill="#38BDF8" opacity="0.95" />
        <circle cx="28" cy="25" r="6" stroke="#818CF8" strokeWidth="1" strokeDasharray="2 2" opacity="0.8" />

        {/* Glare Highlight Arc */}
        <path
          d="M22 20C23.8 17.5 27 16.5 30 17.5"
          stroke="#FFFFFF"
          strokeWidth="1.5"
          strokeLinecap="round"
          opacity="0.85"
        />

        {/* Precision Lens Handle */}
        <path
          d="M36 33L43 40"
          stroke="url(#tlHandleGrad)"
          strokeWidth="3.5"
          strokeLinecap="round"
        />
      </svg>

      {/* Matching Wordmark */}
      {showWordmark && (
        <div className="talentlens-wordmark-container">
          <h1 className="brand-title">TalentLens</h1>
          {subtitle && <p className="talentlens-brand-subtitle">{subtitle}</p>}
        </div>
      )}
    </div>
  );
}
