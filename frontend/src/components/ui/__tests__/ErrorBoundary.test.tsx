import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorBoundary } from '../ErrorBoundary';

function Boom() {
  throw new Error('boom');
}

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


