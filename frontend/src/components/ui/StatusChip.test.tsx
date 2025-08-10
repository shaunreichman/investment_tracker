import React from 'react';
import { render, screen } from '@testing-library/react';
import { StatusChip } from './StatusChip';

describe('StatusChip', () => {
  it('renders with accessible label', () => {
    render(<StatusChip status="active" />);
    expect(screen.getByLabelText(/status: active/i)).toBeInTheDocument();
  });
});


