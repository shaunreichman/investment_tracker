/**
 * Type definitions for ConfirmDialog component
 */

import { ReactNode } from 'react';

/**
 * Action descriptor for dialog buttons
 * Provides typed, flexible action configuration
 */
export interface ActionDescriptor {
  /** Button label text */
  label: string;
  
  /** Visual variant for the button */
  variant: 'error' | 'primary' | 'secondary' | 'outlined';
  
  /** Handler function - can be sync or async */
  onClick: () => void | Promise<void>;
  
  /** Whether the action is in a loading state */
  loading?: boolean;
  
  /** Whether the button should be disabled */
  disabled?: boolean;
  
  /** Optional icon to display before label */
  icon?: ReactNode;
  
  /** Optional test ID for testing */
  testId?: string;
}

/**
 * Overlay event for analytics/telemetry
 */
export interface OverlayEvent {
  /** Unique identifier for this overlay instance */
  overlayId: string;
  
  /** Type of overlay */
  overlayType: 'confirm' | 'form';
  
  /** Action taken (confirm, cancel, escape, backdrop, etc.) */
  action?: string;
  
  /** Timestamp of the event */
  timestamp: Date;
  
  /** Additional context/metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Props for ConfirmDialog component
 */
export interface ConfirmDialogProps {
  /** Whether the dialog is open */
  open: boolean;
  
  /** Dialog title */
  title: string | ReactNode;
  
  /** Optional description text */
  description?: string | ReactNode;
  
  /** Primary confirm action descriptor */
  confirmAction: ActionDescriptor;
  
  /** Optional cancel action descriptor (if not provided, cancel button is hidden) */
  cancelAction?: ActionDescriptor;
  
  /** Optional tertiary action descriptor */
  tertiaryAction?: ActionDescriptor;
  
  /** Callback when dialog opens (for analytics) */
  onOpen?: (event: OverlayEvent) => void;
  
  /** Callback when dialog closes (for analytics) */
  onClose?: (event: OverlayEvent) => void;
  
  /** Callback when an action is triggered (for analytics) */
  onAction?: (event: OverlayEvent) => void;
  
  /** Optional error to display in the dialog */
  error?: string | ReactNode | Error;
  
  /** Unique identifier for this dialog instance (for analytics) */
  overlayId?: string;
  
  /** Maximum width of the dialog */
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  
  /** Whether dialog should be full width */
  fullWidth?: boolean;
  
  /** Custom content to render in dialog body (overrides description) */
  children?: ReactNode;
  
  /** Custom footer content (overrides default action buttons) */
  footer?: ReactNode;
  
  /** Whether to disable backdrop click to close */
  disableBackdropClick?: boolean;
  
  /** Whether to disable escape key to close */
  disableEscapeKeyDown?: boolean;
}

