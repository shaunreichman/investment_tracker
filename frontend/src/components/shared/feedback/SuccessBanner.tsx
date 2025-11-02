import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';
import { CheckCircle as CheckCircleIcon } from '@mui/icons-material';

export interface SuccessBannerProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
}

export const SuccessBanner: React.FC<SuccessBannerProps> = ({ title, subtitle, icon }) => {
  const theme = useTheme();
  
  return (
    <Box 
      role="status" 
      aria-live="polite" 
      sx={{ 
        mb: 3, 
        p: 3, 
        backgroundColor: theme.palette.success.main,
        border: `1px solid ${theme.palette.success.main}`,
        borderRadius: '8px', 
        display: 'flex', 
        alignItems: 'center',
        boxShadow: '0px 4px 12px rgba(6, 165, 140, 0.2)'
      }}
    >
      {icon || <CheckCircleIcon sx={{ mr: 2, color: theme.palette.text.primary, fontSize: '24px' }} />}
      <Box>
        <Typography 
          variant="body1" 
          sx={{ 
            fontWeight: 600, 
            color: theme.palette.text.primary,
            fontSize: '16px',
            mb: subtitle ? 0.5 : 0
          }}
        >
          {title}
        </Typography>
        {subtitle && (
          <Typography 
            variant="body2" 
            sx={{ 
              color: theme.palette.text.primary,
              opacity: 0.9,
              fontSize: '14px'
            }}
          >
            {subtitle}
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default SuccessBanner;

