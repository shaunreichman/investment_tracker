import React from 'react';
import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from '../LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders with provided label', () => {
    render(<LoadingSpinner label="Loading data..." />);
    expect(screen.getByText(/loading data/i)).toBeInTheDocument();
  });
});


