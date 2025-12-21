/**
 * ErrorDisplay Module
 * 
 * Comprehensive error display component with sub-components.
 * 
 * @module shared/ui/feedback/ErrorDisplay
 */

export { ErrorDisplay } from './ErrorDisplay';
export type { ErrorDisplayProps } from './ErrorDisplay.types';

// Export sub-components for advanced usage
export {
  ErrorHeader,
  ErrorMessage,
  ErrorDetails,
  ErrorMetadata,
  ErrorRetry,
} from './components';

export type {
  ErrorHeaderProps,
  ErrorMessageProps,
  ErrorDetailsProps,
  ErrorMetadataProps,
  ErrorRetryProps,
} from './ErrorDisplay.types';

