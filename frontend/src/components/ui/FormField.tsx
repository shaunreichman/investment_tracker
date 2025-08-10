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
    <FormControl fullWidth error={isError} aria-invalid={isError} aria-describedby={helperId}>
      <FormLabel htmlFor={id} required={required || false}>{label}</FormLabel>
      {children}
      {(hint || error) && (
        <FormHelperText id={helperId}>{error || hint}</FormHelperText>
      )}
    </FormControl>
  );
};

export default FormField;


