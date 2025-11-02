/**
 * Type definitions for ConfirmDialog component
 */

export interface ConfirmDialogProps {
  /** Whether the dialog is open */
  open: boolean;
  /** Dialog title */
  title: string;
  /** Optional description text */
  description?: string;
  /** Label for confirm button */
  confirmLabel?: string;
  /** Label for cancel button */
  cancelLabel?: string;
  /** Callback when confirm button is clicked */
  onConfirm: () => void;
  /** Callback when cancel button is clicked or dialog is closed */
  onCancel?: () => void;
  /** Whether the dialog is in a loading state (disables buttons) */
  loading?: boolean;
  /** Whether the confirm button should be disabled */
  disabled?: boolean;
  /** Visual variant for the confirm button */
  confirmVariant?: 'error' | 'primary' | 'secondary';
}

