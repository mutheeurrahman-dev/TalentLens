import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import App from '../src/App.jsx';
import * as api from '../src/api/api.js';

// Mock the API module
vi.mock('../src/api/api.js', () => ({
  getCandidates: vi.fn(),
  matchCandidates: vi.fn(),
  getPresignedUrl: vi.fn(),
  uploadToS3: vi.fn(),
}));

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing and displays the TalentLens brand header', async () => {
    // Mock getCandidates resolving with an empty list
    api.getCandidates.mockResolvedValueOnce([]);

    render(<App />);

    // Check that title appears
    const headerTitle = screen.getByText('TalentLens');
    expect(headerTitle).toBeInTheDocument();

    // Verify sub-components rendered
    expect(screen.getByText('Upload Resume')).toBeInTheDocument();
    expect(screen.getByText('Job Requirements')).toBeInTheDocument();

    // Wait for candidate loading state to resolve
    await waitFor(() => {
      expect(screen.getByText('No candidates yet')).toBeInTheDocument();
    });
  });

  it('renders candidates fetched from the API', async () => {
    const mockCandidates = [
      {
        candidateId: 'cand-123',
        candidateName: 'Jane Doe',
        filename: 'jane_resume.pdf',
        status: 'COMPLETED',
      },
    ];

    api.getCandidates.mockResolvedValueOnce(mockCandidates);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('Jane Doe')).toBeInTheDocument();
      expect(screen.getByText('Candidates (1)')).toBeInTheDocument();
    });
  });

  it('switches between navigation tabs cleanly', async () => {
    api.getCandidates.mockResolvedValueOnce([]);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('TalentLens')).toBeInTheDocument();
    });

    // Navigate to Job Requirements
    const reqTabBtn = screen.getByTestId('tab-requirements');
    fireEvent.click(reqTabBtn);

    // Verify Job Requirements section is active
    expect(screen.getByText('Skills / Job Description')).toBeInTheDocument();
    expect(screen.getByText('Quick Role Presets:')).toBeInTheDocument();

    // Navigate to Resume Upload
    const uploadTabBtn = screen.getByTestId('tab-upload');
    fireEvent.click(uploadTabBtn);

    // Verify Resume Upload section is active
    expect(screen.getByText('Standard PDF resumes up to 10MB')).toBeInTheDocument();

    // Navigate back to Dashboard Overview
    const overviewTabBtn = screen.getByTestId('tab-overview');
    fireEvent.click(overviewTabBtn);

    expect(screen.getByText('Intelligent Resume Screening & Candidate Ranking')).toBeInTheDocument();
  });

  it('dynamically calculates candidate rankings and updates when job criteria change', async () => {
    const mockCandidates = [
      {
        candidateId: 'cand-1',
        candidateName: 'Alice Dev',
        filename: 'alice_resume.pdf',
        status: 'COMPLETED',
      },
      {
        candidateId: 'cand-2',
        candidateName: 'Bob Ops',
        filename: 'bob_resume.pdf',
        status: 'COMPLETED',
      },
    ];

    api.getCandidates.mockResolvedValue(mockCandidates);

    // 1st Match: Junior Full Stack Developer
    api.matchCandidates.mockResolvedValueOnce([
      {
        candidateId: 'cand-1',
        candidateName: 'Alice Dev',
        filename: 'alice_resume.pdf',
        status: 'COMPLETED',
        matchResult: {
          matchPercentage: 85,
          matchedSkills: ['React', 'JavaScript', 'Node.js'],
          missingSkills: ['SQL'],
        },
      },
      {
        candidateId: 'cand-2',
        candidateName: 'Bob Ops',
        filename: 'bob_resume.pdf',
        status: 'COMPLETED',
        matchResult: {
          matchPercentage: 25,
          matchedSkills: ['JavaScript'],
          missingSkills: ['React', 'Node.js', 'SQL'],
        },
      },
    ]);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('Alice Dev')).toBeInTheDocument();
    });

    // Navigate to Job Requirements tab
    fireEvent.click(screen.getByTestId('tab-requirements'));

    // Apply preset or enter requirements
    fireEvent.click(screen.getByText('Junior Full Stack Developer'));

    // Click Match Candidates
    fireEvent.click(screen.getByRole('button', { name: /Match Candidates/i }));

    // Should call API with candidateIds and switch to Candidates view
    await waitFor(() => {
      expect(api.matchCandidates).toHaveBeenCalledWith(
        'Junior Full Stack Developer',
        expect.stringContaining('React, JavaScript'),
        ['cand-1', 'cand-2']
      );
    });

    // Verify Active Job Ranking banner appears
    await waitFor(() => {
      expect(screen.getByText(/Active Job Ranking/i)).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument();
      expect(screen.getByText('25%')).toBeInTheDocument();
    });

    // 2nd Match: Cloud / DevOps Engineer (Bob scores higher now)
    api.matchCandidates.mockResolvedValueOnce([
      {
        candidateId: 'cand-2',
        candidateName: 'Bob Ops',
        filename: 'bob_resume.pdf',
        status: 'COMPLETED',
        matchResult: {
          matchPercentage: 92,
          matchedSkills: ['AWS', 'Docker', 'Kubernetes', 'Linux'],
          missingSkills: ['Terraform'],
        },
      },
      {
        candidateId: 'cand-1',
        candidateName: 'Alice Dev',
        filename: 'alice_resume.pdf',
        status: 'COMPLETED',
        matchResult: {
          matchPercentage: 15,
          matchedSkills: ['Docker'],
          missingSkills: ['AWS', 'Kubernetes', 'Linux', 'Terraform'],
        },
      },
    ]);

    // Go to Job Requirements again
    fireEvent.click(screen.getByTestId('tab-requirements'));

    // Apply DevOps preset
    fireEvent.click(screen.getByText('Cloud / DevOps Engineer'));

    // Click Match Candidates again
    fireEvent.click(screen.getByRole('button', { name: /Match Candidates/i }));

    // Should call API again with new criteria
    await waitFor(() => {
      expect(api.matchCandidates).toHaveBeenLastCalledWith(
        'Cloud / DevOps Engineer',
        expect.stringContaining('AWS, Docker'),
        ['cand-1', 'cand-2']
      );
    });

    // Verify updated rankings and scores
    await waitFor(() => {
      expect(screen.getByText('92%')).toBeInTheDocument();
      expect(screen.getByText('15%')).toBeInTheDocument();
      expect(screen.getByText('Cloud / DevOps Engineer')).toBeInTheDocument();
    });
  });
});
