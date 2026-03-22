/**
 * FormModal Component
 * 
 * A specialized modal wrapper for forms with built-in submission handling,
 * validation states, and unsaved changes protection. Designed to work
 * seamlessly with React Hook Form.
 * 
 * @example
 * ```tsx
 * <FormModal
 *   open={isOpen}
 *   title="Create New Fund"
 *   subtitle="Enter fund details below"
 *   onClose={handleClose}
 *   onSubmit={handleSubmit(onSubmit)}
 *   isSubmitting={isSubmitting}
 *   isValid={isValid}
 *   isDirty={isDirty}
 *   maxWidth="md"
 * >
 *   <FormTextField name="name" label="Fund Name" control={control} />
 *   <FormNumberField name="amount" label="Amount" control={control} />
 * </FormModal>
 * ```
 */

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

import type { FormModalProps } from './FormModal.types';

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

