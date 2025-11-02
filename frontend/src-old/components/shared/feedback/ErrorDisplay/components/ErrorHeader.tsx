/**
 * ErrorHeader Component
 * 
 * Displays error type, severity badges, and action buttons.
 * Pure presentational component.
 */

import React from 'react';
import { Box, Typography, Chip, IconButton, Tooltip, Stack } from '@mui/material';
import {
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  BugReport as BugReportIcon,
} from '@mui/icons-material';

import { getSeverityColor } from '../utils';
import type { ErrorHeaderProps } from '../ErrorDisplay.types';

/**
 * Header section of error display with type, severity, and actions
 */
export const ErrorHeader: React.FC<ErrorHeaderProps> = React.memo(({
  error,
  showDetails,
  hasTechnicalDetails,
  canDismiss,
  showErrorId = false,
  onToggleDetails,
  onDismiss,
}) => {
  const severityColor = getSeverityColor(error.severity);

  return (
    <Box display="flex" alignItems="center" justifyContent="space-between" width="100%">
      <Box display="flex" alignItems="center" gap={1}>
        <Typography variant="subtitle2" component="span">
          {error.type.replace('_', ' ').toUpperCase()}
        </Typography>
        <Chip
          label={error.severity.toUpperCase()}
          size="small"
          color={severityColor}
          variant="outlined"
        />
        {showErrorId && error.id && (
          <Chip
            label={`ID: ${error.id}`}
            size="small"
            variant="outlined"
            icon={<BugReportIcon />}
          />
        )}
      </Box>
      
      <Stack direction="row" spacing={0.5}>
        {hasTechnicalDetails && (
          <Tooltip title={showDetails ? 'Hide Details' : 'Show Details'}>
            <IconButton 
              size="small" 
              onClick={onToggleDetails} 
              color="inherit"
              aria-label={showDetails ? 'Hide technical details' : 'Show technical details'}
              aria-expanded={showDetails}
            >
              {showDetails ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Tooltip>
        )}
        {canDismiss && onDismiss && (
          <Tooltip title="Dismiss">
            <IconButton 
              size="small" 
              onClick={onDismiss} 
              color="inherit"
              aria-label="Dismiss error"
            >
              <CloseIcon />
            </IconButton>
          </Tooltip>
        )}
      </Stack>
    </Box>
  );
});

ErrorHeader.displayName = 'ErrorHeader';

