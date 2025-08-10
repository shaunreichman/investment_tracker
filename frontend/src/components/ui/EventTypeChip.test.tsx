import React from 'react';
import { render, screen } from '@testing-library/react';
import { EventTypeChip } from './EventTypeChip';

describe('EventTypeChip', () => {
  it('renders event type label with aria label', () => {
    render(<EventTypeChip eventType="NAV_UPDATE" />);
    expect(screen.getByLabelText(/event type: nav update/i)).toBeInTheDocument();
  });
});


