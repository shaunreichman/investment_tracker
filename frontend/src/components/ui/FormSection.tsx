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
    <Box component="section" role="region" aria-labelledby={headingId} sx={{ mt: 3 }}>
      <Typography id={headingId} variant="h6" sx={{ mb: description ? 0.5 : 1.5 }}>
        {title}
      </Typography>
      {description && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {description}
        </Typography>
      )}
      <Box display="flex" flexDirection="column" gap={2}>
        {children}
      </Box>
    </Box>
  );
};

export default FormSection;


