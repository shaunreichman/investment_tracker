import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { dockerTheme } from '../../theme/dockerTheme';
import { FormSection } from './FormSection';

describe('FormSection', () => {
  const renderWithTheme = (component: React.ReactElement) => {
    return render(
      <ThemeProvider theme={dockerTheme}>
        {component}
      </ThemeProvider>
    );
  };

  it('renders title and children', () => {
    renderWithTheme(
      <FormSection title="Details">
        <p>Form content</p>
      </FormSection>
    );
    
    expect(screen.getByText('Details')).toBeInTheDocument();
    expect(screen.getByText('Form content')).toBeInTheDocument();
  });

  it('shows subtitle when provided', () => {
    renderWithTheme(
      <FormSection title="Details" subtitle="Provide details">
        <p>Form content</p>
      </FormSection>
    );
    
    expect(screen.getByText('Provide details')).toBeInTheDocument();
  });

  it('shows required indicator when required is true', () => {
    renderWithTheme(
      <FormSection title="Details" required>
        <p>Form content</p>
      </FormSection>
    );
    
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('shows error message when error is provided', () => {
    renderWithTheme(
      <FormSection title="Details" error="This section has errors">
        <p>Form content</p>
      </FormSection>
    );
    
    expect(screen.getByText('This section has errors')).toBeInTheDocument();
  });
});


