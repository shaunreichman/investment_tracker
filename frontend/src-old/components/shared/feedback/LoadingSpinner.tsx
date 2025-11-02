import React from 'react';
import { Box, CircularProgress, Typography, useTheme } from '@mui/material';

export interface LoadingSpinnerProps {
  label?: string;
  size?: number;
  center?: boolean;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  label = 'Loading...',
  size = 40,
  center = true,
}) => {
  const theme = useTheme();
  
  const content = (
    <Box 
      role="status" 
      aria-live="polite" 
      sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center',
        p: 3
      }}
    >
      <CircularProgress 
        size={size} 
        sx={{ 
          mb: 2,
          color: theme.palette.primary.main
        }} 
      />
      <Typography 
        variant="body2" 
        sx={{ 
          color: theme.palette.text.muted,
          fontSize: '14px',
          fontWeight: 500
        }}
      >
        {label}
      </Typography>
    </Box>
  );

  if (center) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: 160,
        backgroundColor: theme.palette.background.paper,
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: '8px',
        m: 2
      }}>
        {content}
      </Box>
    );
  }

  return content;
};

export default LoadingSpinner;

