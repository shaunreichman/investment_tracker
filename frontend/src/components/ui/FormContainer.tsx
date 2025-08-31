import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  CircularProgress,
  useTheme
} from '@mui/material';

export interface FormContainerProps {
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
  /** Custom action buttons (optional) */
  actions?: React.ReactNode;
  /** Whether to show a close confirmation for unsaved changes */
  showCloseConfirmation?: boolean;
  /** Modal size */
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  /** Whether modal should be full width */
  fullWidth?: boolean;
}

export const FormContainer: React.FC<FormContainerProps> = ({
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
  maxWidth = 'md',
  fullWidth = true
}) => {
  const theme = useTheme();

  const handleClose = () => {
    if (showCloseConfirmation && isDirty) {
      const confirmed = window.confirm(
        'You have unsaved changes. Are you sure you want to close?'
      );
      if (!confirmed) return;
    }
    onClose();
  };

  const defaultActions = (
    <>
      <Button 
        onClick={handleClose} 
        disabled={isSubmitting}
        variant="outlined"
      >
        Cancel
      </Button>
      <Button 
        onClick={onSubmit} 
        variant="contained" 
        disabled={isSubmitting || !isValid}
        startIcon={isSubmitting ? <CircularProgress size={20} /> : null}
      >
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </Button>
    </>
  );

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth={maxWidth} 
      fullWidth={fullWidth}
      PaperProps={{
        sx: {
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: '12px',
          boxShadow: '0px 8px 32px rgba(0,0,0,0.4)',
        }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box>
          <Typography variant="h6" component="h2">
            {title}
          </Typography>
          {subtitle && (
            <Typography 
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
          {children}
        </Box>
      </DialogContent>
      
      <DialogActions sx={{ px: 3, pb: 2 }}>
        {actions || defaultActions}
      </DialogActions>
    </Dialog>
  );
};
