import React from 'react';
import { render, screen } from '@testing-library/react';
import { TextField } from '@mui/material';
import { FormField } from './FormField';

describe('FormField', () => {
  it('associates label and helper text', () => {
    render(
      <FormField id="name" label="Name" hint="Enter your name">
        <TextField id="name" />
      </FormField>
    );
    expect(screen.getByLabelText('Name')).toBeInTheDocument();
    expect(screen.getByText(/enter your name/i)).toBeInTheDocument();
  });
});


