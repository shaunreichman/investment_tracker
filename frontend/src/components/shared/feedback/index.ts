// Feedback Components
// Reusable components for loading, error, and success states

export { LoadingSpinner } from './LoadingSpinner';
export type { LoadingSpinnerProps } from './LoadingSpinner';

export { ErrorDisplay } from './ErrorDisplay';
export type { ErrorDisplayProps } from './ErrorDisplay';

export { ErrorToast } from './ErrorToast';
export type { ErrorToastProps } from './ErrorToast';

export { SuccessBanner } from './SuccessBanner';
export type { SuccessBannerProps } from './SuccessBanner';

export { DomainErrorBoundary } from './DomainErrorBoundary';
export type { DomainErrorBoundaryProps, Domain } from './DomainErrorBoundary';

// Export ErrorDisplay sub-components for advanced usage
export {
  ErrorHeader,
  ErrorMessage,
  ErrorDetails,
  ErrorMetadata,
  ErrorRetry,
} from './ErrorDisplay';

