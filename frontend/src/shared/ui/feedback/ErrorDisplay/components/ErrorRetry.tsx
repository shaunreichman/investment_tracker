/**
 * ErrorRetry Component
 * 
 * Displays retry button and retry status information.
 * Handles retry action triggering.
 */

import React from 'react';
import { Box, Button, Typography } from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';
import type { ErrorRetryProps } from '../ErrorDisplay.types';

/**
 * Retry section with button and status
 */
export const ErrorRetry: React.FC<ErrorRetryProps> = React.memo(({
  canRetry,
  isRetrying,
  retryCount,
  maxRetries,
  onRetry,
}) => {
  if (!canRetry) {
    return null;
  }

  return (
    <Box mt={2} display="flex" flexDirection="column" gap={1}>
      <Button
        size="small"
        onClick={onRetry}
        disabled={isRetrying}
        startIcon={
          <RefreshIcon 
            sx={{
              animation: isRetrying ? 'spin 1s linear infinite' : 'none',
              '@keyframes spin': {
                '0%': { transform: 'rotate(0deg)' },
                '100%': { transform: 'rotate(360deg)' },
              },
            }}
          />
        }
        variant="outlined"
      >
        {isRetrying ? 'Retrying...' : 'Retry'}
      </Button>
      
      <Box display="flex" alignItems="center" gap={1}>
        <Typography variant="caption" color="text.secondary">
          Retry {retryCount}/{maxRetries}
        </Typography>
        {isRetrying && (
          <Typography variant="caption" color="primary">
            Retrying...
          </Typography>
        )}
      </Box>
    </Box>
  );
});

ErrorRetry.displayName = 'ErrorRetry';

