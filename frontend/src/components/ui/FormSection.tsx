import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';

export interface FormSectionProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  required?: boolean;
  error?: string;
}

export const FormSection: React.FC<FormSectionProps> = ({ 
  title, 
  subtitle, 
  children, 
  required = false,
  error
}) => {
  const theme = useTheme();
  
  return (
    <Box sx={{ mb: 3 }}>
      <Box sx={{ 
        mb: 2, 
        p: 2, 
        backgroundColor: theme.palette.background.paper,
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: '8px'
      }}>
        <Typography 
          variant="h6" 
          sx={{ 
            color: theme.palette.text.primary,
            fontWeight: 600,
            mb: subtitle ? 1 : 0
          }}
        >
          {title}
          {required && <span style={{ color: theme.palette.error.main }}> *</span>}
        </Typography>
        
        {subtitle && (
          <Typography 
            variant="body2" 
            sx={{ 
              color: theme.palette.text.muted,
              fontSize: '14px'
            }}
          >
            {subtitle}
          </Typography>
        )}
      </Box>
      
      {children}
      
      {error && (
        <Typography 
          variant="body2" 
          sx={{ 
            color: theme.palette.error.main,
            fontSize: '12px',
            mt: 1
          }}
        >
          {error}
        </Typography>
      )}
    </Box>
  );
};

export default FormSection;


