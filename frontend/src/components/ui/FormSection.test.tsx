import React from 'react';
import { render, screen } from '@testing-library/react';
import { FormSection } from './FormSection';

describe('FormSection', () => {
  it('renders title and children', () => {
    render(
      <FormSection title="Details" description="Provide details">
        <div>Child</div>
      </FormSection>
    );
    expect(screen.getByText('Details')).toBeInTheDocument();
    expect(screen.getByText('Provide details')).toBeInTheDocument();
    expect(screen.getByText('Child')).toBeInTheDocument();
  });
});


