/**
 * ErrorDisplay Component
 * 
 * Standardized error display component with retry, auto-dismiss,
 * and technical details functionality.
 * 
 * This is the refactored version using:
 * - useErrorHandler for retry logic and state
 * - useErrorAutoDismiss for auto-dismiss functionality
 * - useErrorDetailsToggle for details visibility
 * - Smaller sub-components for better maintainability
 */

import React, { useCallback } from 'react';
import { Alert, AlertTitle } from '@mui/material';

import { useErrorHandler } from '@/shared/hooks/core/error';
import { useErrorAutoDismiss, useErrorDetailsToggle } from '@/shared/hooks/errors';

import { ErrorHeader, ErrorMessage, ErrorDetails, ErrorRetry } from './components';
import { getErrorColor, getSeverityIcon } from './utils';

import type { ErrorDisplayProps } from './ErrorDisplay.types';

// ============================================================================
// ERROR DISPLAY COMPONENT
// ============================================================================

/**
 * Comprehensive error display component
 * 
 * @example
 * ```tsx
 * <ErrorDisplay
 *   error={error}
 *   onDismiss={() => setError(null)}
 *   canDismiss
 *   autoDismiss
 *   dismissDelay={5000}
 *   onRetry={handleRetry}
 *   maxRetries={3}
 * />
 * ```
 */
export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  showDetails: initialShowDetails = false,
  canDismiss = true,
  autoDismiss = false,
  dismissDelay = 5000,
  maxRetries = 3,
  onRetry,
  onDismiss,
  onToggleDetails,
  customMessage,
  showErrorId = false,
  sx = {},
}) => {
  // ============================================================================
  // HOOKS
  // ============================================================================
  
  // Error handler hook for retry logic
  const {
    isRetrying,
    retryCount,
    canRetry,
    retry,
  } = useErrorHandler({ maxRetries });

  // Error details toggle hook
  const { showDetails, toggleDetails } = useErrorDetailsToggle(initialShowDetails);

  // Auto-dismiss hook
  useErrorAutoDismiss(autoDismiss, dismissDelay, onDismiss, error);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================
  
  const handleToggleDetails = useCallback(() => {
    toggleDetails();
    if (onToggleDetails) {
      onToggleDetails(!showDetails);
    }
  }, [toggleDetails, onToggleDetails, showDetails]);

  const handleRetry = useCallback(() => {
    if (onRetry) {
      // Use the error handler's retry mechanism
      retry(async () => {
        await onRetry();
      });
    }
  }, [onRetry, retry]);

  // ============================================================================
  // EARLY RETURN
  // ============================================================================
  
  if (!error) {
    return null;
  }

  // ============================================================================
  // COMPUTED VALUES
  // ============================================================================
  
  const errorColor = getErrorColor(error.type);
  const SeverityIcon = getSeverityIcon(error.severity);
  const displayMessage = customMessage || error.userMessage;
  const hasTechnicalDetails = !!(error.stack || error.message);

  // ============================================================================
  // RENDER
  // ============================================================================
  
  return (
    <Alert
      role="alert"
      severity={errorColor}
      icon={<SeverityIcon />}
      sx={{
        ...sx,
        '& .rotating': {
          animation: 'spin 1s linear infinite',
        },
        '@keyframes spin': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      }}
    >
      <AlertTitle>
        <ErrorHeader
          error={error}
          showDetails={showDetails}
          hasTechnicalDetails={hasTechnicalDetails}
          canDismiss={canDismiss}
          showErrorId={showErrorId}
          onToggleDetails={handleToggleDetails}
          {...(onDismiss && { onDismiss })}
        />
      </AlertTitle>
      
      <ErrorMessage message={displayMessage} />
      
      {error.retryable && onRetry && (
        <ErrorRetry
          canRetry={canRetry}
          isRetrying={isRetrying}
          retryCount={retryCount}
          maxRetries={maxRetries}
          onRetry={handleRetry}
        />
      )}
      
      {hasTechnicalDetails && (
        <ErrorDetails error={error} show={showDetails} />
      )}
    </Alert>
  );
};

ErrorDisplay.displayName = 'ErrorDisplay';

export default ErrorDisplay;

