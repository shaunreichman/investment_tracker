import React from 'react';
import { FormControl, FormLabel, FormHelperText } from '@mui/material';

export interface FormFieldProps {
  id: string;
  label: string;
  error?: string | null;
  hint?: string;
  required?: boolean;
  children: React.ReactNode;
}

export const FormField: React.FC<FormFieldProps> = ({ id, label, error, hint, required, children }) => {
  const helperId = hint || error ? `${id}-help` : undefined;
  const isError = Boolean(error);

  return (
    <FormControl 
      fullWidth 
      error={isError} 
      aria-invalid={isError} 
      aria-describedby={helperId}
      sx={{ mb: 3 }}
    >
      <FormLabel 
        htmlFor={id} 
        required={required || false}
        sx={{
          color: '#FFFFFF',
          fontWeight: 600,
          fontSize: '14px',
          mb: 1,
          '&.Mui-focused': {
            color: '#2496ED'
          },
          '&.Mui-error': {
            color: '#F85149'
          }
        }}
      >
        {label}
      </FormLabel>
      {children}
      {(hint || error) && (
        <FormHelperText 
          id={helperId}
          sx={{
            color: isError ? '#F85149' : '#8B949E',
            fontSize: '12px',
            fontWeight: 500,
            mt: 0.5
          }}
        >
          {error || hint}
        </FormHelperText>
      )}
    </FormControl>
  );
};

export default FormField;


