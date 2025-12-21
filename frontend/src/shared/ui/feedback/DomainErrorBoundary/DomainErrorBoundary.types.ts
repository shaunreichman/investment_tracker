/**
 * Type definitions for DomainErrorBoundary
 */

import { ReactNode } from 'react';
import { type ErrorContext } from '@/shared/utils/errors';

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
}

export type Domain = DomainErrorBoundaryProps['domain'];

