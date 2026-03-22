/**
 * Domain-Specific Error Boundary
 * 
 * Enterprise-grade error boundary with domain-specific error handling and recovery.
 * Provides context-aware error messages, error tracking, and recovery options.
 * 
 * Features:
 * - Domain-specific error messages (fund, entity, company, banking, rates)
 * - Error loop detection (prevents infinite error states)
 * - Full error logging integration (errorLogger)
 * - Error count tracking and history
 * - Configurable technical details display
 * - Recovery actions (retry, navigate to safety)
 * 
 * Usage:
 *   <DomainErrorBoundary domain="fund" onReset={handleReset}>
 *     <FundComponent />
 *   </DomainErrorBoundary>
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Button, Paper, Typography, Alert, Stack } from '@mui/material';
import { Error as ErrorIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import { errorLogger, createErrorInfo, type ErrorContext } from '@/shared/utils/errors';
import type { ErrorInfo as NormalizedErrorInfo } from '@/shared/types/errors';

// ============================================================================
// DOMAIN ERROR BOUNDARY PROPS
// ============================================================================

export interface DomainErrorBoundaryProps {
  /** Child components to protect */
  children: ReactNode;
  
  /** Domain name for context-specific handling */
  domain: 'fund' | 'entity' | 'company' | 'banking' | 'rates' | 'general';
  
  /** Custom fallback UI */
  fallback?: ReactNode;
  
  /** Callback when user requests reset/retry */
  onReset?: () => void;
  
  /** Additional error context */
  context?: Partial<ErrorContext>;
  
  /** Whether to show technical error details */
  showDetails?: boolean;
  
  /** Optional telemetry/analytics callback for error capture */
  onErrorCaptured?: (error: NormalizedErrorInfo, context: ErrorContext) => void;
}

interface DomainErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorCount: number;
}

// ============================================================================
// DOMAIN-SPECIFIC ERROR MESSAGES
// ============================================================================

const getDomainErrorMessage = (domain: DomainErrorBoundaryProps['domain']): {
  title: string;
  message: string;
  suggestion: string;
} => {
  switch (domain) {
    case 'fund':
      return {
        title: 'Fund Component Error',
        message: 'An error occurred while loading fund information.',
        suggestion: 'This might be a temporary issue. Try refreshing the fund data or navigating back to the fund list.'
      };
    case 'entity':
      return {
        title: 'Entity Component Error',
        message: 'An error occurred while loading entity information.',
        suggestion: 'This might be a temporary issue. Try refreshing the page or returning to the entity list.'
      };
    case 'company':
      return {
        title: 'Company Component Error',
        message: 'An error occurred while loading company information.',
        suggestion: 'This might be a temporary issue. Try refreshing the company data or navigating back to the company list.'
      };
    case 'banking':
      return {
        title: 'Banking Component Error',
        message: 'An error occurred while loading banking information.',
        suggestion: 'This might be a temporary issue. Try refreshing the page or returning to the banking overview.'
      };
    case 'rates':
      return {
        title: 'Rates Component Error',
        message: 'An error occurred while loading rate information.',
        suggestion: 'This might be a temporary issue. Try refreshing the rates data.'
      };
    case 'general':
    default:
      return {
        title: 'Component Error',
        message: 'An unexpected error occurred.',
        suggestion: 'This might be a temporary issue. Try refreshing the page or navigating back.'
      };
  }
};

// ============================================================================
// DOMAIN ERROR BOUNDARY COMPONENT
// ============================================================================

export class DomainErrorBoundary extends Component<
  DomainErrorBoundaryProps,
  DomainErrorBoundaryState
> {
  constructor(props: DomainErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0
    };
  }

  static getDerivedStateFromError(error: Error): Partial<DomainErrorBoundaryState> {
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Normalize error using error utilities
    const normalizedError = createErrorInfo(error);
    
    // Create error context
    const errorContext: ErrorContext = {
      context: `${this.props.domain}_error_boundary`,
      metadata: {
        domain: this.props.domain,
        componentStack: errorInfo.componentStack,
        errorCount: this.state.errorCount + 1,
        ...this.props.context?.metadata
      },
      ...this.props.context
    };
    
    // Log error with domain context
    errorLogger.logError(normalizedError, errorContext);
    
    // Call telemetry/analytics callback if provided
    if (this.props.onErrorCaptured) {
      this.props.onErrorCaptured(normalizedError, errorContext);
    }

    this.setState(prevState => ({
      errorInfo,
      errorCount: prevState.errorCount + 1
    }));

    // Check for error loop (too many errors in short time)
    if (this.state.errorCount > 5) {
      console.error(
        `[${this.props.domain.toUpperCase()}] Error boundary caught too many errors. This might indicate an error loop.`
      );
      errorLogger.logWarning(
        `Error loop detected in ${this.props.domain} domain`,
        { context: `${this.props.domain}_error_boundary` }
      );
    }
  }

  componentDidUpdate(_prevProps: DomainErrorBoundaryProps, prevState: DomainErrorBoundaryState): void {
    // Reset error count if component recovered
    if (prevState.hasError && !this.state.hasError) {
      this.setState({ errorCount: 0 });
    }
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });

    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const domainMessages = getDomainErrorMessage(this.props.domain);
      const { error, errorInfo } = this.state;

      return (
        <Paper
          role="alert"
          aria-live="assertive"
          sx={{
            p: 3,
            m: 2,
            border: '2px solid',
            borderColor: 'error.main'
          }}
        >
          <Stack spacing={2}>
            {/* Error Icon and Title */}
            <Box display="flex" alignItems="center" gap={1}>
              <ErrorIcon color="error" sx={{ fontSize: 32 }} />
              <Typography variant="h6" color="error">
                {domainMessages.title}
              </Typography>
            </Box>

            {/* Error Message */}
            <Alert severity="error">
              <Typography variant="body1" gutterBottom>
                {domainMessages.message}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {domainMessages.suggestion}
              </Typography>
            </Alert>

            {/* Action Buttons */}
            <Box display="flex" gap={2}>
              <Button
                variant="contained"
                color="primary"
                onClick={this.handleReset}
                startIcon={<RefreshIcon />}
              >
                Try Again
              </Button>
              <Button
                variant="outlined"
                onClick={() => window.location.href = '/'}
              >
                Go to Dashboard
              </Button>
            </Box>

            {/* Technical Details (if enabled) */}
            {this.props.showDetails && error && (
              <Box
                sx={{
                  mt: 2,
                  p: 2,
                  bgcolor: 'grey.100',
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: 'grey.300'
                }}
              >
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  Technical Details:
                </Typography>
                <Typography
                  variant="body2"
                  fontFamily="monospace"
                  fontSize="0.75rem"
                  sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}
                >
                  {error.toString()}
                </Typography>
                {errorInfo && errorInfo.componentStack && (
                  <Typography
                    variant="body2"
                    fontFamily="monospace"
                    fontSize="0.7rem"
                    color="text.secondary"
                    sx={{
                      mt: 1,
                      maxHeight: '200px',
                      overflow: 'auto',
                      whiteSpace: 'pre-wrap'
                    }}
                  >
                    {errorInfo.componentStack}
                  </Typography>
                )}
              </Box>
            )}

            {/* Error Count Warning */}
            {this.state.errorCount > 3 && (
              <Alert severity="warning">
                <Typography variant="body2">
                  Multiple errors detected ({this.state.errorCount}). If this persists, please
                  refresh the page or contact support.
                </Typography>
              </Alert>
            )}
          </Stack>
        </Paper>
      );
    }

    return this.props.children;
  }
}

export default DomainErrorBoundary;

