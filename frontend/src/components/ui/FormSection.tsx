import React from 'react';
import { Box, Typography } from '@mui/material';

export interface FormSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

export const FormSection: React.FC<FormSectionProps> = ({ title, description, children }) => {
  const headingId = `${title.replace(/\s+/g, '-').toLowerCase()}-heading`;

  return (
    <Box 
      component="section" 
      role="region" 
      aria-labelledby={headingId} 
      sx={{ 
        mt: 4,
        p: 3,
        backgroundColor: '#1F2937',
        border: '1px solid #303234',
        borderRadius: '8px'
      }}
    >
      <Typography 
        id={headingId} 
        variant="h5" 
        sx={{ 
          mb: description ? 1 : 2,
          color: '#FFFFFF',
          fontWeight: 600,
          fontSize: '18px'
        }}
      >
        {title}
      </Typography>
      {description && (
        <Typography 
          variant="body2" 
          sx={{ 
            mb: 3,
            color: '#8B949E',
            fontSize: '14px',
            lineHeight: 1.5
          }}
        >
          {description}
        </Typography>
      )}
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 2
      }}>
        {children}
      </Box>
    </Box>
  );
};

export default FormSection;


