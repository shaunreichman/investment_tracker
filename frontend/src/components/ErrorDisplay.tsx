// Standardized Error Display Component
// This component provides consistent error UI across the application
// with error-specific styling, icons, and actions

import React from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Button,
  Collapse,
  IconButton,
  Typography,
  Chip,
  Stack,
  Tooltip
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  BugReport as BugReportIcon
} from '@mui/icons-material';
import { ErrorInfo, ErrorType, ErrorSeverity } from '../types/errors';

// ============================================================================
// ERROR DISPLAY PROPS
// ============================================================================

/**
 * Props for the ErrorDisplay component
 */
export interface ErrorDisplayProps {
  /** Error information to display */
  error: ErrorInfo | null;
  
  /** Whether to show technical error details */
  showDetails?: boolean;
  
  /** Whether retry functionality should be available */
  canRetry?: boolean;
  
  /** Whether the error can be dismissed */
  canDismiss?: boolean;
  
  /** Whether to auto-dismiss the error */
  autoDismiss?: boolean;
  
  /** Delay before auto-dismissing (in milliseconds) */
  dismissDelay?: number;
  
  /** Custom error display variant */
  variant?: 'inline' | 'modal' | 'toast' | 'banner';
  
  /** Whether retry is currently in progress */
  isRetrying?: boolean;
  
  /** Retry attempt count */
  retryCount?: number;
  
  /** Maximum retry attempts */
  maxRetries?: number;
  
  /** Callback when retry is requested */
  onRetry?: () => void;
  
  /** Callback when error is dismissed */
  onDismiss?: () => void;
  
  /** Callback when details are toggled */
  onToggleDetails?: (show: boolean) => void;
  
  /** Custom error message override */
  customMessage?: string;
  
  /** Whether to show error ID for debugging */
  showErrorId?: boolean;
  
  /** Custom styling */
  sx?: any;
}

// ============================================================================
// ERROR ICON MAPPING
// ============================================================================

/**
 * Gets the appropriate icon for an error type
 */
const getErrorIcon = (type: ErrorType) => {
  switch (type) {
    case ErrorType.NETWORK:
      return <RefreshIcon />;
    case ErrorType.VALIDATION:
      return <WarningIcon />;
    case ErrorType.AUTHENTICATION:
    case ErrorType.AUTHORIZATION:
      return <ErrorIcon />;
    case ErrorType.NOT_FOUND:
      return <InfoIcon />;
    case ErrorType.SERVER:
      return <ErrorIcon />;
    case ErrorType.UNKNOWN:
    default:
      return <ErrorIcon />;
  }
};

/**
 * Gets the appropriate icon for an error severity
 */
const getSeverityIcon = (severity: ErrorSeverity) => {
  switch (severity) {
    case ErrorSeverity.LOW:
      return <InfoIcon />;
    case ErrorSeverity.MEDIUM:
      return <WarningIcon />;
    case ErrorSeverity.HIGH:
    case ErrorSeverity.CRITICAL:
      return <ErrorIcon />;
    default:
      return <ErrorIcon />;
  }
};

// ============================================================================
// ERROR COLOR MAPPING
// ============================================================================

/**
 * Gets the appropriate color for an error type
 */
const getErrorColor = (type: ErrorType): 'error' | 'warning' | 'info' => {
  switch (type) {
    case ErrorType.NETWORK:
      return 'warning';
    case ErrorType.VALIDATION:
      return 'warning';
    case ErrorType.AUTHENTICATION:
    case ErrorType.AUTHORIZATION:
      return 'error';
    case ErrorType.NOT_FOUND:
      return 'info';
    case ErrorType.SERVER:
      return 'error';
    case ErrorType.UNKNOWN:
    default:
      return 'error';
  }
};

/**
 * Gets the appropriate color for an error severity
 */
const getSeverityColor = (severity: ErrorSeverity): 'error' | 'warning' | 'info' => {
  switch (severity) {
    case ErrorSeverity.LOW:
      return 'info';
    case ErrorSeverity.MEDIUM:
      return 'warning';
    case ErrorSeverity.HIGH:
    case ErrorSeverity.CRITICAL:
      return 'error';
    default:
      return 'error';
  }
};

// ============================================================================
// ERROR DISPLAY COMPONENT
// ============================================================================

/**
 * Standardized error display component
 */
export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  showDetails = false,
  canRetry = true,
  canDismiss = true,
  autoDismiss = false,
  dismissDelay = 5000,
  variant = 'inline',
  isRetrying = false,
  retryCount = 0,
  maxRetries = 3,
  onRetry,
  onDismiss,
  onToggleDetails,
  customMessage,
  showErrorId = false,
  sx = {}
}) => {
  // ============================================================================
  // STATE MANAGEMENT
  // ============================================================================
  
  const [showTechnicalDetails, setShowTechnicalDetails] = React.useState(showDetails);
  const [autoDismissTimer, setAutoDismissTimer] = React.useState<NodeJS.Timeout | null>(null);

  // ============================================================================
  // AUTO-DISMISS HANDLING
  // ============================================================================
  
  React.useEffect(() => {
    if (autoDismiss && error && onDismiss) {
      const timer = setTimeout(() => {
        onDismiss();
      }, dismissDelay);
      
      setAutoDismissTimer(timer);
      
      return () => {
        if (timer) clearTimeout(timer);
      };
    }
  }, [autoDismiss, error, dismissDelay, onDismiss]);

  // ============================================================================
  // CLEANUP
  // ============================================================================
  
  React.useEffect(() => {
    return () => {
      if (autoDismissTimer) {
        clearTimeout(autoDismissTimer);
      }
    };
  }, [autoDismissTimer]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================
  
  const handleRetry = () => {
    if (onRetry && canRetry && !isRetrying) {
      onRetry();
    }
  };

  const handleDismiss = () => {
    if (onDismiss && canDismiss) {
      onDismiss();
    }
  };

  const handleToggleDetails = () => {
    const newShowDetails = !showTechnicalDetails;
    setShowTechnicalDetails(newShowDetails);
    if (onToggleDetails) {
      onToggleDetails(newShowDetails);
    }
  };

  // ============================================================================
  // EARLY RETURNS
  // ============================================================================
  
  if (!error) {
    return null;
  }

  // ============================================================================
  // COMPUTED VALUES
  // ============================================================================
  
  const errorColor = getErrorColor(error.type);
  const severityColor = getSeverityColor(error.severity);
  const errorIcon = getErrorIcon(error.type);
  const severityIcon = getSeverityIcon(error.severity);
  const displayMessage = customMessage || error.userMessage;
  const canActuallyRetry = canRetry && error.retryable && retryCount < maxRetries;

  // ============================================================================
  // RENDER FUNCTIONS
  // ============================================================================
  
  const renderErrorHeader = () => (
    <Box display="flex" alignItems="center" justifyContent="space-between" width="100%">
      <Box display="flex" alignItems="center" gap={1}>
        {errorIcon}
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
      <Box display="flex" alignItems="center" gap={0.5}>
        {canActuallyRetry && (
          <Tooltip title={isRetrying ? 'Retrying...' : 'Retry'}>
            <IconButton
              size="small"
              onClick={handleRetry}
              disabled={isRetrying}
              color="primary"
            >
              <RefreshIcon className={isRetrying ? 'rotating' : ''} />
            </IconButton>
          </Tooltip>
        )}
        {canDismiss && (
          <Tooltip title="Dismiss">
            <IconButton size="small" onClick={handleDismiss} color="inherit">
              <CloseIcon />
            </IconButton>
          </Tooltip>
        )}
      </Box>
    </Box>
  );

  const renderErrorDetails = () => (
    <Collapse in={showTechnicalDetails}>
      <Box mt={1} p={1} bgcolor="background.paper" borderRadius={1} border={1} borderColor="divider">
        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
          Technical Details:
        </Typography>
        <Typography variant="body2" fontFamily="monospace" whiteSpace="pre-wrap">
          {error.message}
        </Typography>
        {error.stack && (
          <>
            <Typography variant="caption" color="text.secondary" display="block" mt={1}>
              Stack Trace:
            </Typography>
            <Typography variant="body2" fontFamily="monospace" fontSize="0.75rem" whiteSpace="pre-wrap">
              {error.stack}
            </Typography>
          </>
        )}
        <Box mt={1} display="flex" gap={1} flexWrap="wrap">
          <Chip label={`Type: ${error.type}`} size="small" variant="outlined" />
          <Chip label={`Severity: ${error.severity}`} size="small" variant="outlined" />
          <Chip label={`Retryable: ${error.retryable ? 'Yes' : 'No'}`} size="small" variant="outlined" />
          {error.code && (
            <Chip label={`Code: ${error.code}`} size="small" variant="outlined" />
          )}
          <Chip 
            label={`Time: ${error.timestamp.toLocaleTimeString()}`} 
            size="small" 
            variant="outlined" 
          />
        </Box>
      </Box>
    </Collapse>
  );

  const renderRetryInfo = () => {
    if (!canActuallyRetry) return null;
    
    return (
      <Box mt={1} display="flex" alignItems="center" gap={1}>
        <Typography variant="caption" color="text.secondary">
          Retry {retryCount}/{maxRetries}
        </Typography>
        {isRetrying && (
          <Typography variant="caption" color="primary">
            Retrying...
          </Typography>
        )}
      </Box>
    );
  };

  // ============================================================================
  // MAIN RENDER
  // ============================================================================
  
  return (
    <Alert
      severity={errorColor}
      icon={severityIcon}
      action={
        <Stack direction="row" spacing={0.5}>
          {error.stack && (
            <Tooltip title={showTechnicalDetails ? 'Hide Details' : 'Show Details'}>
              <IconButton size="small" onClick={handleToggleDetails} color="inherit">
                {showTechnicalDetails ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Tooltip>
          )}
          {canActuallyRetry && (
            <Button
              size="small"
              onClick={handleRetry}
              disabled={isRetrying}
              startIcon={<RefreshIcon className={isRetrying ? 'rotating' : ''} />}
              variant="outlined"
            >
              {isRetrying ? 'Retrying...' : 'Retry'}
            </Button>
          )}
          {canDismiss && (
            <IconButton size="small" onClick={handleDismiss} color="inherit">
              <CloseIcon />
            </IconButton>
          )}
        </Stack>
      }
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
      <AlertTitle>{renderErrorHeader()}</AlertTitle>
      <Typography variant="body2" component="div">
        {displayMessage}
      </Typography>
      {renderRetryInfo()}
      {renderErrorDetails()}
    </Alert>
  );
};

// ============================================================================
// EXPORT
// ============================================================================

export default ErrorDisplay; 