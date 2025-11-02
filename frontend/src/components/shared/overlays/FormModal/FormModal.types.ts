/**
 * Type definitions for FormModal component
 */

export interface FormModalProps {
  /** Whether the modal is open */
  open: boolean;
  /** Modal title */
  title: string;
  /** Optional subtitle */
  subtitle?: string;
  /** Function to call when modal is closed */
  onClose: () => void;
  /** Function to call when form is submitted */
  onSubmit: () => void;
  /** Whether the form is currently submitting */
  isSubmitting?: boolean;
  /** Whether the form is valid and can be submitted */
  isValid?: boolean;
  /** Whether the form has unsaved changes */
  isDirty?: boolean;
  /** Form content */
  children: React.ReactNode;
  /** Custom action buttons (optional, overrides default Submit/Cancel) */
  actions?: React.ReactNode;
  /** Whether to show a close confirmation for unsaved changes */
  showCloseConfirmation?: boolean;
  /** Modal size */
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  /** Whether modal should be full width */
  fullWidth?: boolean;
}

