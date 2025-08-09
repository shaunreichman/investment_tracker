import React from 'react';
import { Box, Typography } from '@mui/material';
import { CheckCircle as CheckCircleIcon } from '@mui/icons-material';

export interface SuccessBannerProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
}

export const SuccessBanner: React.FC<SuccessBannerProps> = ({ title, subtitle, icon }) => {
  return (
    <Box role="status" aria-live="polite" sx={{ mb: 2, p: 2, bgcolor: 'success.light', borderRadius: 1, display: 'flex', alignItems: 'center' }}>
      {icon || <CheckCircleIcon color="success" sx={{ mr: 1 }} />}
      <Box>
        <Typography variant="body1" fontWeight="medium" color="success.main">
          {title}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="success.main">
            {subtitle}
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default SuccessBanner;


