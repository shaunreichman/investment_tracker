import React from 'react';
import { render, screen } from '@testing-library/react';
import { SuccessBanner } from './SuccessBanner';

describe('SuccessBanner', () => {
  it('renders title and subtitle', () => {
    render(<SuccessBanner title="Done" subtitle="All good" />);
    expect(screen.getByText('Done')).toBeInTheDocument();
    expect(screen.getByText('All good')).toBeInTheDocument();
  });
});


