/**
 * ErrorMetadata Component
 * 
 * Displays error metadata chips (type, severity, retryable, code, timestamp).
 * Pure presentational component.
 */

import React from 'react';
import { Box, Chip } from '@mui/material';
import type { ErrorMetadataProps } from '../ErrorDisplay.types';

/**
 * Metadata chips for technical error information
 */
export const ErrorMetadata: React.FC<ErrorMetadataProps> = React.memo(({ error }) => (
  <Box mt={1} display="flex" gap={1} flexWrap="wrap">
    <Chip 
      label={`Type: ${error.type}`} 
      size="small" 
      variant="outlined" 
    />
    <Chip 
      label={`Severity: ${error.severity}`} 
      size="small" 
      variant="outlined" 
    />
    <Chip 
      label={`Retryable: ${error.retryable ? 'Yes' : 'No'}`} 
      size="small" 
      variant="outlined" 
    />
    {error.code && (
      <Chip 
        label={`Code: ${error.code}`} 
        size="small" 
        variant="outlined" 
      />
    )}
    <Chip 
      label={`Time: ${error.timestamp.toLocaleTimeString()}`} 
      size="small" 
      variant="outlined" 
    />
  </Box>
));

ErrorMetadata.displayName = 'ErrorMetadata';

