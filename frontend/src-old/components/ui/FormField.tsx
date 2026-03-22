import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';

export interface FormFieldProps {
  label: string;
  required?: boolean;
  error?: string | undefined;
  children: React.ReactNode;
  helperText?: string;
  disabled?: boolean;
  variant?: 'standard' | 'outlined' | 'filled';
  size?: 'small' | 'medium' | 'large';
  /** Whether the field has been touched/interacted with */
  touched?: boolean | undefined;
  /** Whether to show error only when touched */
  showErrorOnlyWhenTouched?: boolean;
}

export const FormField: React.FC<FormFieldProps> = ({ 
  label, 
  required = false, 
  error, 
  children, 
  helperText,
  disabled = false,
  variant = 'standard',
  size = 'medium',
  touched = false,
  showErrorOnlyWhenTouched = true
}) => {
  const theme = useTheme();
  
  // Determine if we should show the error
  const shouldShowError = error && (!showErrorOnlyWhenTouched || touched);
  
  // Determine if we should show helper text
  const shouldShowHelperText = helperText && !shouldShowError;
  
  return (
    <Box sx={{ mb: 2 }}>
      <Typography 
        variant="body2" 
        component="label"
        sx={{ 
          color: theme.palette.text.primary,
          fontWeight: 500,
          mb: 1,
          display: 'flex',
          alignItems: 'center',
          gap: 0.5,
          cursor: disabled ? 'not-allowed' : 'default'
        }}
      >
        {label}
        {required && (
          <span 
            style={{ 
              color: theme.palette.error.main,
              fontSize: '14px',
              fontWeight: 'bold'
            }}
            aria-label="required"
          >
            *
          </span>
        )}
      </Typography>
      
      <Box sx={{ mb: 1 }}>
        {children}
      </Box>
      
      {/* Error message */}
      {shouldShowError && (
        <Typography 
          variant="caption" 
          sx={{ 
            color: theme.palette.error.main,
            fontSize: '12px',
            display: 'block',
            mt: 0.5,
            fontWeight: 500
          }}
          role="alert"
          aria-live="polite"
        >
          {error}
        </Typography>
      )}
      
      {/* Helper text */}
      {shouldShowHelperText && (
        <Typography 
          variant="caption" 
          sx={{ 
            color: theme.palette.text.secondary,
            fontSize: '12px',
            display: 'block',
            mt: 0.5
          }}
        >
          {helperText}
        </Typography>
      )}
    </Box>
  );
};

export default FormField;

