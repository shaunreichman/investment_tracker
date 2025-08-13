import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';

export interface FormFieldProps {
  label: string;
  required?: boolean;
  error?: string;
  children: React.ReactNode;
  helperText?: string;
  disabled?: boolean;
}

export const FormField: React.FC<FormFieldProps> = ({ 
  label, 
  required = false, 
  error, 
  children, 
  helperText,
  disabled = false
}) => {
  const theme = useTheme();
  
  return (
    <Box sx={{ mb: 2 }}>
      <Typography 
        variant="body2" 
        sx={{ 
          color: theme.palette.text.primary,
          fontWeight: 500,
          mb: 1,
          display: 'flex',
          alignItems: 'center',
          gap: 0.5
        }}
      >
        {label}
        {required && (
          <span style={{ 
            color: theme.palette.error.main,
            fontSize: '14px'
          }}>
            *
          </span>
        )}
      </Typography>
      
      <Box sx={{ mb: 1 }}>
        {children}
      </Box>
      
      {(error || helperText) && (
        <Typography 
          variant="caption" 
          sx={{ 
            color: error ? theme.palette.error.main : theme.palette.text.muted,
            fontSize: '12px',
            display: 'block',
            mt: 0.5
          }}
        >
          {error || helperText}
        </Typography>
      )}
    </Box>
  );
};


