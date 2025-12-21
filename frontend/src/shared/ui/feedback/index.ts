// ============================================================================
// FEEDBACK COMPONENTS - BARREL EXPORT
// ============================================================================

// Loading and Success components
export { LoadingSpinner } from './LoadingSpinner';
export type { LoadingSpinnerProps } from './LoadingSpinner';

export { SuccessBanner } from './SuccessBanner';
export type { SuccessBannerProps } from './SuccessBanner';

// Error handling components
export { DomainErrorBoundary } from './DomainErrorBoundary';
export type { DomainErrorBoundaryProps, Domain } from './DomainErrorBoundary';

export { ErrorDisplay } from './ErrorDisplay';
export type { ErrorDisplayProps } from './ErrorDisplay';

// Export ErrorDisplay sub-components for advanced usage
export {
  ErrorHeader,
  ErrorMessage,
  ErrorDetails,
  ErrorMetadata,
  ErrorRetry,
} from './ErrorDisplay';

export type {
  ErrorHeaderProps,
  ErrorMessageProps,
  ErrorDetailsProps,
  ErrorMetadataProps,
  ErrorRetryProps,
} from './ErrorDisplay';

