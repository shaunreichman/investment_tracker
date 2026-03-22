/**
 * ConfirmDialog Component
 * 
 * A reusable confirmation dialog for destructive or important actions.
 * Typically used for delete confirmations, irreversible operations, or
 * actions that require explicit user consent.
 * 
 * @example
 * ```tsx
 * <ConfirmDialog
 *   open={isOpen}
 *   title="Delete Fund"
 *   description="Are you sure you want to delete this fund? This action cannot be undone."
 *   confirmLabel="Delete"
 *   cancelLabel="Cancel"
 *   onConfirm={handleDelete}
 *   onCancel={() => setIsOpen(false)}
 *   loading={isDeleting}
 *   confirmVariant="error"
 * />
 * ```
 */

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  CircularProgress,
  useTheme,
} from '@mui/material';

import type { ConfirmDialogProps } from './ConfirmDialog.types';

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  title,
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm,
  onCancel,
  loading = false,
  disabled = false,
  confirmVariant = 'error',
}) => {
  const theme = useTheme();
  
  const titleId = 'confirm-dialog-title';
  const descId = description ? 'confirm-dialog-description' : undefined;

  return (
    <Dialog 
      open={open} 
      onClose={onCancel || (() => {})} 
      aria-labelledby={titleId} 
      {...(descId && { 'aria-describedby': descId })}
      PaperProps={{
        sx: {
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: '12px',
          boxShadow: '0px 8px 32px rgba(0,0,0,0.4)',
          minWidth: '400px',
          maxWidth: '500px'
        }
      }}
    >
      <DialogTitle 
        id={titleId}
        sx={{
          color: theme.palette.text.primary,
          fontWeight: 600,
          fontSize: '20px',
          borderBottom: `1px solid ${theme.palette.divider}`,
          backgroundColor: theme.palette.background.sidebar,
          borderRadius: '12px 12px 0 0'
        }}
      >
        {title}
      </DialogTitle>
      
      {description && (
        <DialogContent sx={{ p: 3 }}>
          <DialogContentText 
            id={descId}
            sx={{
              color: theme.palette.text.muted,
              fontSize: '16px',
              lineHeight: 1.5
            }}
          >
            {description}
          </DialogContentText>
        </DialogContent>
      )}
      
      <DialogActions sx={{ p: 3, pt: 2, gap: 2 }}>
        {onCancel && cancelLabel && (
          <Button 
            onClick={onCancel} 
            disabled={loading}
            variant="outlined"
            sx={{
              borderColor: theme.palette.divider,
              color: theme.palette.text.secondary,
              '&:hover': {
                borderColor: theme.palette.text.muted,
                backgroundColor: theme.palette.background.sidebarHover
              },
              '&:disabled': {
                borderColor: theme.palette.text.disabled || theme.palette.text.muted,
                color: theme.palette.text.disabled || theme.palette.text.muted
              },
              px: 3,
              py: 1
            }}
          >
            {cancelLabel}
          </Button>
        )}
        
        <Button
          onClick={onConfirm}
          variant="contained"
          disabled={loading || disabled}
          startIcon={loading ? <CircularProgress size={18} sx={{ color: theme.palette.text.primary }} /> : null}
          sx={{
            backgroundColor: theme.palette.error.main,
            '&:hover': {
              backgroundColor: theme.palette.error.dark
            },
            '&:disabled': {
              backgroundColor: theme.palette.text.disabled || theme.palette.text.muted
            },
            px: 3,
            py: 1,
            fontWeight: 500
          }}
        >
          {loading ? 'Working...' : confirmLabel}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

