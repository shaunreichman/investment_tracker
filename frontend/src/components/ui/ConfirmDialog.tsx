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
    <Dialog 
      open={open} 
      onClose={onCancel} 
      aria-labelledby={titleId} 
      {...(descId && { 'aria-describedby': descId })}
      PaperProps={{
        sx: {
          backgroundColor: '#1F2937',
          border: '1px solid #303234',
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
          color: '#FFFFFF',
          fontWeight: 600,
          fontSize: '20px',
          borderBottom: '1px solid #303234',
          backgroundColor: '#070b0d',
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
              color: '#8B949E',
              fontSize: '16px',
              lineHeight: 1.5
            }}
          >
            {description}
          </DialogContentText>
        </DialogContent>
      )}
      
      <DialogActions sx={{ p: 3, pt: 2, gap: 2 }}>
        <Button 
          onClick={onCancel} 
          disabled={loading}
          variant="outlined"
          sx={{
            borderColor: '#303234',
            color: '#C9D1D9',
            '&:hover': {
              borderColor: '#8B949E',
              backgroundColor: '#19222a'
            },
            '&:disabled': {
              borderColor: '#6B7280',
              color: '#6B7280'
            },
            px: 3,
            py: 1
          }}
        >
          {cancelLabel}
        </Button>
        
        <Button
          onClick={onConfirm}
          variant="contained"
          disabled={loading || disabled}
          startIcon={loading ? <CircularProgress size={18} sx={{ color: '#FFFFFF' }} /> : null}
          sx={{
            backgroundColor: '#F85149',
            '&:hover': {
              backgroundColor: '#DC3545'
            },
            '&:disabled': {
              backgroundColor: '#6B7280'
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

export default ConfirmDialog;


