import React, { useEffect } from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorBoundary } from '../ErrorBoundary';

const Boom: React.FC = () => {
  useEffect(() => {
    throw new Error('boom');
  }, []);
  return null;
};

describe('ErrorBoundary', () => {
  it('renders fallback and resets on click', async () => {
    const onReset = jest.fn();
    render(
      <ErrorBoundary fallbackText="Fallback" onReset={onReset}>
        <Boom />
      </ErrorBoundary>
    );
    expect(screen.getByText(/fallback/i)).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /try again/i }));
    expect(onReset).toHaveBeenCalled();
  });
});


