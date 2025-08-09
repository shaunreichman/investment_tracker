import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  CircularProgress,
} from '@mui/material';

export interface ConfirmDialogProps {
  open: boolean;
  title: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  loading?: boolean;
  disabled?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  title,
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  loading = false,
  disabled = false,
  onConfirm,
  onCancel,
}) => {
  const titleId = 'confirm-dialog-title';
  const descId = description ? 'confirm-dialog-description' : undefined;

  return (
    <Dialog open={open} onClose={onCancel} aria-labelledby={titleId} aria-describedby={descId}>
      <DialogTitle id={titleId}>{title}</DialogTitle>
      {description && (
        <DialogContent>
          <DialogContentText id={descId}>{description}</DialogContentText>
        </DialogContent>
      )}
      <DialogActions>
        <Button onClick={onCancel} disabled={loading}> {cancelLabel} </Button>
        <Button
          onClick={onConfirm}
          variant="contained"
          color="error"
          disabled={loading || disabled}
          startIcon={loading ? <CircularProgress size={18} /> : null}
        >
          {loading ? 'Working...' : confirmLabel}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmDialog;


