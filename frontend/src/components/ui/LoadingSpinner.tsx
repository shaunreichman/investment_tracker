import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

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
          color: '#2496ED'
        }} 
      />
      <Typography 
        variant="body2" 
        sx={{ 
          color: '#8B949E',
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
        backgroundColor: '#1F2937',
        border: '1px solid #303234',
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


