import React, { useEffect } from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorBoundary } from '../ErrorBoundary';

// Component that intentionally throws an error for testing
const Boom: React.FC = () => {
  useEffect(() => {
    throw new Error('boom');
  }, []);
  return null;
};

describe('ErrorBoundary', () => {
  // Suppress console.error only for this specific test suite
  let originalError: typeof console.error;
  
  beforeEach(() => {
    // Store original console.error
    originalError = console.error;
    // Suppress error boundary logging during this specific test
    console.error = jest.fn();
  });

  afterEach(() => {
    // Restore console.error after each test
    console.error = originalError;
  });

  it('renders fallback and resets on click', async () => {
    const onReset = jest.fn();
    
    render(
      <ErrorBoundary fallbackText="Fallback" onReset={onReset}>
        <Boom />
      </ErrorBoundary>
    );
    
    // Wait for error boundary to catch the error and render fallback
    await waitFor(() => {
      expect(screen.getByText(/fallback/i)).toBeInTheDocument();
    });
    
    // Verify error was logged (but suppressed during test)
    expect(console.error).toHaveBeenCalledWith('ErrorBoundary caught error', expect.any(Error));
    
    // Test reset functionality
    const resetButton = screen.getByRole('button', { name: /try again/i });
    await userEvent.click(resetButton);
    
    expect(onReset).toHaveBeenCalledTimes(1);
  });
});


