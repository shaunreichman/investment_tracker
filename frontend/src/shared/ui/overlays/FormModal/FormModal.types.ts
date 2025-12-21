/**
 * Type definitions for FormModal component
 */

import { ReactNode } from 'react';
import { UseFormReturn, FieldValues } from 'react-hook-form';
import type { OverlayEvent } from '../ConfirmDialog/ConfirmDialog.types';

/**
 * Props for FormModal component
 */
export interface FormModalProps {
  /** Whether the modal is open */
  open: boolean;
  
  /** Modal title */
  title: string | ReactNode;
  
  /** Optional subtitle */
  subtitle?: string | ReactNode;
  
  /** Function to call when modal should close */
  onClose: () => void;
  
  /** Function to call when form is submitted */
  onSubmit: () => void | Promise<void>;
  
  /** Whether the form is currently submitting */
  isSubmitting?: boolean;
  
  /** Whether the form is valid and can be submitted */
  isValid?: boolean;
  
  /** Whether the form has unsaved changes */
  isDirty?: boolean;
  
  /** Form content */
  children: ReactNode;
  
  /** Custom action buttons (optional, overrides default Submit/Cancel) */
  actions?: ReactNode;
  
  /** Whether to show a close confirmation for unsaved changes */
  showCloseConfirmation?: boolean;
  
  /** Custom confirmation message for unsaved changes */
  closeConfirmationMessage?: string;
  
  /** Modal size */
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  
  /** Whether modal should be full width */
  fullWidth?: boolean;
  
  /** Optional error to display in the modal */
  error?: string | ReactNode | Error;
  
  /** React Hook Form instance (optional - can use useFormContext instead) */
  form?: UseFormReturn<FieldValues>;
  
  /** Callback when modal opens (for analytics) */
  onOpen?: (event: OverlayEvent) => void;
  
  /** Callback when modal closes (for analytics) */
  onCloseEvent?: (event: OverlayEvent) => void;
  
  /** Callback when form is submitted (for analytics) */
  onSubmitEvent?: (event: OverlayEvent) => void;
  
  /** Callback when error occurs (for analytics) */
  onError?: (event: OverlayEvent & { error: Error | string }) => void;
  
  /** Unique identifier for this modal instance (for analytics) */
  overlayId?: string;
  
  /** Whether to disable backdrop click to close */
  disableBackdropClick?: boolean;
  
  /** Whether to disable escape key to close */
  disableEscapeKeyDown?: boolean;
}

