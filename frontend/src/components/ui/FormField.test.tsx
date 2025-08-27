import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { dockerTheme } from '../../theme/dockerTheme';
import { FormField } from './FormField';

describe('FormField', () => {
  const renderWithTheme = (component: React.ReactElement) => {
    return render(
      <ThemeProvider theme={dockerTheme}>
        {component}
      </ThemeProvider>
    );
  };

  it('renders label and children', () => {
    renderWithTheme(
      <FormField label="Name" helperText="Enter your name">
        <input />
      </FormField>
    );
    
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Enter your name')).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('shows required indicator when required is true', () => {
    renderWithTheme(
      <FormField label="Name" required>
        <input />
      </FormField>
    );
    
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('shows error message when error is provided', () => {
    renderWithTheme(
      <FormField label="Name" error="This field is required">
        <input />
      </FormField>
    );
    
    expect(screen.getByText('This field is required')).toBeInTheDocument();
  });
});


