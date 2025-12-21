/**
 * ConfirmDialog Component
 * 
 * Enterprise-grade confirmation dialog with typed action descriptors,
 * loading/error states, analytics callbacks, and full accessibility support.
 * 
 * @example
 * ```tsx
 * <ConfirmDialog
 *   open={isOpen}
 *   title="Delete Fund"
 *   description="This action cannot be undone."
 *   confirmAction={{
 *     label: "Delete",
 *     variant: "error",
 *     onClick: handleDelete,
 *     loading: isDeleting
 *   }}
 *   cancelAction={{
 *     label: "Cancel",
 *     variant: "outlined",
 *     onClick: () => setIsOpen(false)
 *   }}
 *   onOpen={(event) => analytics.track('dialog_opened', event)}
 *   onClose={(event) => analytics.track('dialog_closed', event)}
 * />
 * ```
 */

import React, { useEffect, useRef, useCallback, useMemo } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  CircularProgress,
  Alert,
  Box,
  useTheme,
} from '@mui/material';
import type { ConfirmDialogProps, OverlayEvent, ActionDescriptor } from './ConfirmDialog.types';

/**
 * Generate unique overlay ID if not provided
 */
const generateOverlayId = (): string => {
  return `confirm-dialog-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
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
    overlayType: 'confirm',
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

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  title,
  description,
  confirmAction,
  cancelAction,
  tertiaryAction,
  onOpen,
  onClose,
  onAction,
  error,
  overlayId: providedOverlayId,
  maxWidth = 'sm',
  fullWidth = true,
  children,
  footer,
  disableBackdropClick = false,
  disableEscapeKeyDown = false,
}) => {
  const theme = useTheme();
  const overlayIdRef = useRef<string>(providedOverlayId || generateOverlayId());
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const dialogTitleId = 'confirm-dialog-title';
  const dialogDescId = description ? 'confirm-dialog-description' : undefined;

  // Track previous focus when dialog opens
  useEffect(() => {
    if (open) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      
      // Fire onOpen event
      if (onOpen) {
        const event = createOverlayEvent(overlayIdRef.current, 'open');
        onOpen(event);
      }
    } else if (previousFocusRef.current) {
      // Return focus when dialog closes
      // Use setTimeout to ensure dialog is fully closed
      setTimeout(() => {
        previousFocusRef.current?.focus();
        previousFocusRef.current = null;
      }, 0);
    }
  }, [open, onOpen]);

  // Handle dialog close
  const handleClose = useCallback((reason: 'backdropClick' | 'escapeKeyDown' | 'cancel') => {
    if (reason === 'backdropClick' && disableBackdropClick) {
      return;
    }
    if (reason === 'escapeKeyDown' && disableEscapeKeyDown) {
      return;
    }

    const action = reason === 'backdropClick' ? 'backdrop' : reason === 'escapeKeyDown' ? 'escape' : 'cancel';
    const event = createOverlayEvent(overlayIdRef.current, action);
    
    if (onClose) {
      onClose(event);
    }

    // Call cancel action if provided
    if (reason === 'cancel' && cancelAction) {
      cancelAction.onClick();
    }
  }, [disableBackdropClick, disableEscapeKeyDown, onClose, cancelAction]);

  // Handle action click
  const handleActionClick = useCallback(async (
    action: typeof confirmAction | typeof cancelAction | typeof tertiaryAction,
    actionName: string
  ) => {
    if (!action || action.loading || action.disabled) {
      return;
    }

    // Fire onAction event
    if (onAction) {
      const event = createOverlayEvent(overlayIdRef.current, actionName);
      onAction(event);
    }

    // Execute action
    try {
      await action.onClick();
    } catch (err) {
      // Error handling is up to the consumer
      // We just ensure the event is fired
      console.error('Error in dialog action:', err);
    }
  }, [onAction]);

  // Memoize button variant mapping
  const getButtonVariant = useCallback((variant: 'error' | 'primary' | 'secondary' | 'outlined') => {
    switch (variant) {
      case 'error':
        return 'contained';
      case 'primary':
        return 'contained';
      case 'secondary':
        return 'contained';
      case 'outlined':
        return 'outlined';
      default:
        return 'contained';
    }
  }, []);

  // Memoize button color mapping
  const getButtonColor = useCallback((variant: 'error' | 'primary' | 'secondary' | 'outlined') => {
    switch (variant) {
      case 'error':
        return 'error';
      case 'primary':
        return 'primary';
      case 'secondary':
        return 'secondary';
      case 'outlined':
        return 'inherit';
      default:
        return 'primary';
    }
  }, []);

  // Render action button
  const renderActionButton = useCallback((
    action: typeof confirmAction | typeof cancelAction | typeof tertiaryAction,
    actionName: string
  ) => {
    if (!action) return null;

    const buttonVariant = getButtonVariant(action.variant);
    const buttonColor = getButtonColor(action.variant);

    return (
      <Button
        key={actionName}
        onClick={() => handleActionClick(action, actionName)}
        variant={buttonVariant}
        color={buttonColor}
        disabled={action.loading || action.disabled || false}
        startIcon={
          action.loading ? (
            <CircularProgress size={18} sx={{ color: 'inherit' }} />
          ) : (
            action.icon
          )
        }
        data-testid={action.testId || `dialog-action-${actionName}`}
        sx={{
          ...(action.variant === 'error' && {
            backgroundColor: theme.palette.error.main,
            '&:hover': {
              backgroundColor: theme.palette.error.dark,
            },
            '&:disabled': {
              backgroundColor: theme.palette.action.disabledBackground,
            },
          }),
          px: 3,
          py: 1,
          fontWeight: 500,
        }}
      >
        {action.loading ? 'Working...' : action.label}
      </Button>
    );
  }, [confirmAction, cancelAction, tertiaryAction, getButtonVariant, getButtonColor, handleActionClick, theme]);

  // Default actions order: cancel, tertiary, confirm
  const defaultActions = useMemo(() => {
    const actions: React.ReactNode[] = [];
    
    if (cancelAction) {
      actions.push(renderActionButton(cancelAction, 'cancel'));
    }
    
    if (tertiaryAction) {
      actions.push(renderActionButton(tertiaryAction, 'tertiary'));
    }
    
    actions.push(renderActionButton(confirmAction, 'confirm'));
    
    return actions;
  }, [cancelAction, tertiaryAction, confirmAction, renderActionButton]);

  return (
    <Dialog
      open={open}
      onClose={(_, reason) => handleClose(reason)}
      maxWidth={maxWidth}
      fullWidth={fullWidth}
      aria-labelledby={dialogTitleId}
      {...(dialogDescId && { 'aria-describedby': dialogDescId })}
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
      <DialogTitle
        id={dialogTitleId}
        sx={{
          color: theme.palette.text.primary,
          fontWeight: 600,
          fontSize: '20px',
          borderBottom: `1px solid ${theme.palette.divider}`,
          backgroundColor: theme.palette.background.default,
          borderRadius: '12px 12px 0 0',
          pb: 2,
        }}
      >
        {title}
      </DialogTitle>

      {(description || children || error) && (
        <DialogContent sx={{ p: 3 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {formatError(error)}
            </Alert>
          )}
          
          {children ? (
            <Box>{children}</Box>
          ) : description ? (
            <DialogContentText
              id={dialogDescId}
              sx={{
                color: theme.palette.text.secondary,
                fontSize: '16px',
                lineHeight: 1.5,
              }}
            >
              {description}
            </DialogContentText>
          ) : null}
        </DialogContent>
      )}

      <DialogActions sx={{ p: 3, pt: 2, gap: 2 }}>
        {footer || defaultActions}
      </DialogActions>
    </Dialog>
  );
};

