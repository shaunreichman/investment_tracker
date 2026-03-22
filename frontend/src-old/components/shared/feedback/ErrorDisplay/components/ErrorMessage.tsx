/**
 * ErrorMessage Component
 * 
 * Displays the user-friendly error message.
 * Pure presentational component.
 */

import React from 'react';
import { Typography } from '@mui/material';
import type { ErrorMessageProps } from '../ErrorDisplay.types';

/**
 * User-friendly error message display
 */
export const ErrorMessage: React.FC<ErrorMessageProps> = React.memo(({ message }) => (
  <Typography variant="body2" component="div">
    {message}
  </Typography>
));

ErrorMessage.displayName = 'ErrorMessage';

