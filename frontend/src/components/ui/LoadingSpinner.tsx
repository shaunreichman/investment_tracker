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
    <Box role="status" aria-live="polite" display="flex" flexDirection="column" alignItems="center">
      <CircularProgress size={size} sx={{ mb: 1 }} />
      <Typography variant="body2" color="text.secondary">{label}</Typography>
    </Box>
  );

  if (center) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={160}>
        {content}
      </Box>
    );
  }

  return content;
};

export default LoadingSpinner;


