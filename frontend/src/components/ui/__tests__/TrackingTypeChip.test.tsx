import React from 'react';
import { render, screen } from '@testing-library/react';
import { TrackingTypeChip } from '../TrackingTypeChip';

describe('TrackingTypeChip', () => {
  it('renders nav_based label', () => {
    render(<TrackingTypeChip trackingType="nav_based" />);
    expect(screen.getByLabelText(/tracking: nav_based/i)).toBeInTheDocument();
  });
  it('renders cost_based label', () => {
    render(<TrackingTypeChip trackingType="cost_based" />);
    expect(screen.getByLabelText(/tracking: cost_based/i)).toBeInTheDocument();
  });
});


