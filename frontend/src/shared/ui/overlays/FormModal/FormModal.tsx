/**
 * FormModal Component
 * 
 * Enterprise-grade form modal with React Hook Form integration,
 * dirty-state guard, standardized submit/cancel slots, and analytics callbacks.
 * 
 * @example
 * ```tsx
 * const form = useForm<FormData>({ schema, defaultValues });
 * 
 * <FormModal
 *   open={isOpen}
 *   title="Create Fund"
 *   onClose={() => setIsOpen(false)}
 *   onSubmit={form.handleSubmit(onSubmit)}
 *   isSubmitting={isPending}
 *   isValid={form.formState.isValid}
 *   isDirty={form.formState.isDirty}
 *   form={form}
 * >
 *   <FormTextField name="name" control={form.control} />
 * </FormModal>
 * ```
 */

import React, { useEffect, useRef, useCallback, useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  CircularProgress,
  Alert,
  useTheme,
} from '@mui/material';
import { useFormContext } from 'react-hook-form';
import type { FormModalProps } from './FormModal.types';
import { ConfirmDialog } from '../ConfirmDialog';
import type { ActionDescriptor, OverlayEvent } from '../ConfirmDialog';

/**
 * Generate unique overlay ID if not provided
 */
const generateOverlayId = (): string => {
  return `form-modal-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Create overlay event for analytics
 */
const createOverlayEvent = (
  overlayId: string,
  action: string,
  metadata?: Record<string, unknown>
): OverlayEvent => {
  const event: OverlayEvent = {
    overlayId,
    overlayType: 'form',
    action,
    timestamp: new Date(),
  };
  if (metadata) {
    event.metadata = metadata;
  }
  return event;
};

/**
 * Format error for display
 */
const formatError = (error: string | React.ReactNode | Error): React.ReactNode => {
  if (typeof error === 'string') {
    return error;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return error;
};

export const FormModal: React.FC<FormModalProps> = ({
  open,
  title,
  subtitle,
  onClose,
  onSubmit,
  isSubmitting = false,
  isValid = true,
  isDirty = false,
  children,
  actions,
  showCloseConfirmation = true,
  closeConfirmationMessage = 'You have unsaved changes. Are you sure you want to close?',
  maxWidth = 'md',
  fullWidth = true,
  error,
  form,
  onOpen,
  onCloseEvent,
  onSubmitEvent,
  onError,
  overlayId: providedOverlayId,
  disableBackdropClick = false,
  disableEscapeKeyDown = false,
}) => {
  const theme = useTheme();
  const overlayIdRef = useRef<string>(providedOverlayId || generateOverlayId());
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const [showCloseConfirm, setShowCloseConfirm] = useState(false);
  
  // Try to get form from context if not provided
  const formContext = useFormContext();
  const formInstance = form || formContext;

  // Track previous focus when modal opens
  useEffect(() => {
    if (open) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      
      // Fire onOpen event
      if (onOpen) {
        const event = createOverlayEvent(overlayIdRef.current, 'open');
        onOpen(event);
      }
    } else if (previousFocusRef.current) {
      // Return focus when modal closes
      setTimeout(() => {
        previousFocusRef.current?.focus();
        previousFocusRef.current = null;
      }, 0);
    }
  }, [open, onOpen]);

  // Handle modal close with dirty state guard
  const handleClose = useCallback((reason: 'backdropClick' | 'escapeKeyDown' | 'cancel') => {
    if (reason === 'backdropClick' && disableBackdropClick) {
      return;
    }
    if (reason === 'escapeKeyDown' && disableEscapeKeyDown) {
      return;
    }

    // Check for unsaved changes
    if (showCloseConfirmation && isDirty && !showCloseConfirm) {
      setShowCloseConfirm(true);
      return;
    }

    // Proceed with close
    const action = reason === 'backdropClick' ? 'backdrop' : reason === 'escapeKeyDown' ? 'escape' : 'cancel';
    const event = createOverlayEvent(overlayIdRef.current, action);
    
    if (onCloseEvent) {
      onCloseEvent(event);
    }

    setShowCloseConfirm(false);
    onClose();
  }, [showCloseConfirmation, isDirty, showCloseConfirm, disableBackdropClick, disableEscapeKeyDown, onClose, onCloseEvent]);

  // Handle form submission
  const handleSubmit = useCallback(async () => {
    try {
      // Fire onSubmitEvent before submission
      if (onSubmitEvent) {
        const event = createOverlayEvent(overlayIdRef.current, 'submit');
        onSubmitEvent(event);
      }

      await onSubmit();
    } catch (err) {
      // Fire onError event
      if (onError) {
        const errorEvent = createOverlayEvent(overlayIdRef.current, 'error', {
          error: err instanceof Error ? err.message : String(err),
        }) as OverlayEvent & { error: Error | string };
        errorEvent.error = err instanceof Error ? err : String(err);
        onError(errorEvent);
      }
      
      // Re-throw to allow consumer to handle
      throw err;
    }
  }, [onSubmit, onSubmitEvent, onError]);

  // Default actions
  const defaultActions = (
    <>
      <Button
        onClick={() => handleClose('cancel')}
        disabled={isSubmitting}
        variant="outlined"
        sx={{
          borderColor: theme.palette.divider,
          color: theme.palette.text.secondary,
          '&:hover': {
            borderColor: theme.palette.text.muted,
            backgroundColor: theme.palette.background.default,
          },
        }}
      >
        Cancel
      </Button>
      <Button
        onClick={handleSubmit}
        variant="contained"
        disabled={isSubmitting || !isValid}
        startIcon={isSubmitting ? <CircularProgress size={20} /> : null}
        sx={{
          px: 3,
          py: 1,
          fontWeight: 500,
        }}
      >
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </Button>
    </>
  );

  // Close confirmation dialog actions
  const closeConfirmActions: {
    confirm: ActionDescriptor;
    cancel: ActionDescriptor;
  } = {
    confirm: {
      label: 'Discard Changes',
      variant: 'error',
      onClick: () => {
        setShowCloseConfirm(false);
        onClose();
      },
    },
    cancel: {
      label: 'Keep Editing',
      variant: 'outlined',
      onClick: () => setShowCloseConfirm(false),
    },
  };

  return (
    <>
      <Dialog
        open={open && !showCloseConfirm}
        onClose={(_, reason) => handleClose(reason)}
        maxWidth={maxWidth}
        fullWidth={fullWidth}
        aria-labelledby="form-modal-title"
        {...(subtitle && { 'aria-describedby': 'form-modal-subtitle' })}
        aria-modal="true"
        PaperProps={{
          sx: {
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
            borderRadius: '12px',
            boxShadow: '0px 8px 32px rgba(0,0,0,0.4)',
          },
        }}
      >
        <DialogTitle id="form-modal-title" sx={{ pb: 1 }}>
          <Box>
            <Typography variant="h6" component="h2">
              {title}
            </Typography>
            {subtitle && (
              <Typography
                id="form-modal-subtitle"
                variant="body2"
                color="text.secondary"
                sx={{ mt: 0.5 }}
              >
                {subtitle}
              </Typography>
            )}
          </Box>
        </DialogTitle>

        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {formatError(error)}
              </Alert>
            )}
            {children}
          </Box>
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2 }}>
          {actions || defaultActions}
        </DialogActions>
      </Dialog>

      {/* Close confirmation dialog */}
      <ConfirmDialog
        open={showCloseConfirm}
        title="Unsaved Changes"
        description={closeConfirmationMessage}
        confirmAction={closeConfirmActions.confirm}
        cancelAction={closeConfirmActions.cancel}
        overlayId={`${overlayIdRef.current}-close-confirm`}
      />
    </>
  );
};

