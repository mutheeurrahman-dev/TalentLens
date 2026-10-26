import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import CloudArchitecture from '../src/components/CloudArchitecture.jsx';

describe('CloudArchitecture Component', () => {
  it('renders the cloud architecture panel with title and AWS region', () => {
    render(<CloudArchitecture />);

    expect(screen.getByText('Cloud Architecture & Process Flow')).toBeInTheDocument();
    expect(screen.getByText('AWS ap-south-1')).toBeInTheDocument();
    expect(screen.getByText('Serverless SAM')).toBeInTheDocument();
  });

  it('renders all key process flow steps including API Gateway, S3, SQS, Lambda, and pypdf', () => {
    render(<CloudArchitecture />);

    // Check process steps
    expect(screen.getByText('PDF Upload')).toBeInTheDocument();
    expect(screen.getAllByText('Amazon API Gateway').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Amazon S3').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Amazon SQS').length).toBeGreaterThan(0);
    expect(screen.getAllByText('AWS Lambda').length).toBeGreaterThan(0);
    expect(screen.getByText('pypdf Engine')).toBeInTheDocument();
    expect(screen.getAllByText('Amazon DynamoDB').length).toBeGreaterThan(0);
    expect(screen.getByText('Dynamic Ranking')).toBeInTheDocument();
  });

  it('toggles collapsible panel when toggle button is clicked', () => {
    render(<CloudArchitecture />);

    const toggleBtn = screen.getByRole('button', { name: /Collapse ▲/i });
    expect(toggleBtn).toBeInTheDocument();

    // Collapse
    fireEvent.click(toggleBtn);
    expect(screen.getByRole('button', { name: /View Architecture ▼/i })).toBeInTheDocument();
    expect(screen.queryByText('End-to-End Event-Driven Process Flow:')).not.toBeInTheDocument();

    // Expand again
    fireEvent.click(screen.getByRole('button', { name: /View Architecture ▼/i }));
    expect(screen.getByText('End-to-End Event-Driven Process Flow:')).toBeInTheDocument();
  });
});
