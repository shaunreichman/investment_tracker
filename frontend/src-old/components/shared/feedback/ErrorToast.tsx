// Error Toast Component
// A simple toast notification for error messages

import React from 'react';
import { Snackbar, Alert, AlertTitle, Box, IconButton } from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { ErrorInfo } from '../../../types/errors';

// ============================================================================
// ERROR TOAST PROPS
// ============================================================================

export interface ErrorToastProps {
  /** Error information to display */
  error: ErrorInfo | null;
  
  /** Whether the toast is open */
  open: boolean;
  
  /** Callback when toast is closed */
  onClose: () => void;
  
  /** Auto-hide duration in milliseconds (0 = don't auto-hide) */
  autoHideDuration?: number;
  
  /** Custom error message override */
  customMessage?: string;
  
  /** Whether to show error details */
  showDetails?: boolean;
}

// ============================================================================
// ERROR TOAST COMPONENT
// ============================================================================

/**
 * Simple error toast component for quick error notifications
 */
export const ErrorToast: React.FC<ErrorToastProps> = ({
  error,
  open,
  onClose,
  autoHideDuration = 6000,
  customMessage,
  showDetails = false
}) => {
  if (!error) return null;

  const handleClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    onClose();
  };

  return (
    <Snackbar
      open={open}
      autoHideDuration={autoHideDuration}
      onClose={handleClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
    >
      <Alert
        onClose={handleClose}
        severity="error"
        sx={{ width: '100%' }}
        action={
          <IconButton
            aria-label="close"
            color="inherit"
            size="small"
            onClick={handleClose}
          >
            <CloseIcon fontSize="inherit" />
          </IconButton>
        }
      >
        <AlertTitle>{error.type.replace('_', ' ').toUpperCase()}</AlertTitle>
        {customMessage || error.userMessage}
        {showDetails && error.message && (
          <Box mt={1} fontSize="0.75rem" color="text.secondary">
            {error.message}
          </Box>
        )}
      </Alert>
    </Snackbar>
  );
};

export default ErrorToast;

