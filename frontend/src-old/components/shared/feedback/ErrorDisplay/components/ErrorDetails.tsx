/**
 * ErrorDetails Component
 * 
 * Collapsible section displaying technical error details.
 * Includes error message, stack trace, and metadata.
 */

import React from 'react';
import { Box, Collapse, Typography } from '@mui/material';
import { ErrorMetadata } from './ErrorMetadata';
import type { ErrorDetailsProps } from '../ErrorDisplay.types';

/**
 * Technical error details section with stack trace and metadata
 */
export const ErrorDetails: React.FC<ErrorDetailsProps> = React.memo(({ error, show }) => (
  <Collapse in={show}>
    <Box 
      mt={1} 
      p={1} 
      bgcolor="background.paper" 
      borderRadius={1} 
      border={1} 
      borderColor="divider"
    >
      <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
        Technical Details:
      </Typography>
      <Typography variant="body2" fontFamily="monospace" whiteSpace="pre-wrap">
        {error.message}
      </Typography>
      
      {error.stack && (
        <>
          <Typography 
            variant="caption" 
            color="text.secondary" 
            display="block" 
            mt={1}
          >
            Stack Trace:
          </Typography>
          <Typography 
            variant="body2" 
            fontFamily="monospace" 
            fontSize="0.75rem" 
            whiteSpace="pre-wrap"
          >
            {error.stack}
          </Typography>
        </>
      )}
      
      <ErrorMetadata error={error} />
    </Box>
  </Collapse>
));

ErrorDetails.displayName = 'ErrorDetails';

