import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  CircularProgress,
  Typography,
  Paper
} from '@mui/material';
import { ErrorDisplay } from './ErrorDisplay';
import { useErrorHandler } from '../hooks/useErrorHandler';
import { Add as AddIcon, CheckCircle as CheckCircleIcon } from '@mui/icons-material';
import { useCreateEntity } from '../hooks/useEntities';

interface CreateEntityModalProps {
  open: boolean;
  onClose: () => void;
  onEntityCreated: (entity: { id: number; name: string }) => void;
}

interface ValidationErrors {
  name?: string;
  description?: string;
  tax_jurisdiction?: string;
}

const CreateEntityModal: React.FC<CreateEntityModalProps> = ({
  open,
  onClose,
  onEntityCreated
}) => {
  const [success, setSuccess] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});

  // Form fields
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    tax_jurisdiction: 'AU'
  });

  // Centralized API hook
  const createEntity = useCreateEntity();

  // Centralized error handler
  const { error, setError, clearError } = useErrorHandler();

  // Handle errors and success from hooks
  useEffect(() => {
    if (createEntity.error) {
      setError(createEntity.error);
    }
  }, [createEntity.error, setError]);

  useEffect(() => {
    if (createEntity.data) {
      setSuccess(true);
      setTimeout(() => {
        onEntityCreated({
          id: createEntity.data!.id,
          name: createEntity.data!.name
        });
        onClose();
        setSuccess(false);
        setFormData({
          name: '',
          description: '',
          tax_jurisdiction: 'AU'
        });
        setValidationErrors({});
      }, 2000);
    }
  }, [createEntity.data, onEntityCreated, onClose]);

  // Validation rules
  const validateField = (field: string, value: string): string | undefined => {
    switch (field) {
      case 'name':
        if (!value.trim()) return 'Entity name is required';
        if (value.trim().length < 2) return 'Entity name must be at least 2 characters';
        if (value.trim().length > 255) return 'Entity name must be less than 255 characters';
        if (!/^[a-zA-Z0-9\s\-_()]+$/.test(value.trim())) {
          return 'Entity name can only contain letters, numbers, spaces, hyphens, underscores, and parentheses';
        }
        break;
      
      case 'description':
        if (value && value.trim().length > 1000) {
          return 'Description must be less than 1000 characters';
        }
        break;
    }
    return undefined;
  };

  const validateForm = useCallback((): boolean => {
    const errors: ValidationErrors = {};
    
    // Required fields
    if (!formData.name.trim()) {
      errors.name = 'Entity name is required';
    }
    
    // Field-specific validation
    const nameError = validateField('name', formData.name);
    if (nameError) errors.name = nameError;
    
    const descriptionError = validateField('description', formData.description);
    if (descriptionError) errors.description = descriptionError;
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  }, [formData]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Real-time validation
    const error = validateField(field, value);
    setValidationErrors(prev => ({
      ...prev,
      [field]: error
    }));
  };

  const handleSubmit = async () => {
    // Clear any previous errors
    clearError();
    
    // Validate form
    if (!validateForm()) {
      setError('Please fix the validation errors before submitting');
      return;
    }

    const payload = {
      name: formData.name.trim(),
      description: formData.description.trim() || '',
      tax_jurisdiction: formData.tax_jurisdiction
    };

    await createEntity.mutate(payload);
  };

  const handleClose = () => {
    if (!createEntity.loading) {
      onClose();
      clearError();
      setSuccess(false);
      setValidationErrors({});
      // Clear form data when closing
      setFormData({
        name: '',
        description: '',
        tax_jurisdiction: 'AU'
      });
    }
  };

  const isFormValid = () => {
    return formData.name.trim() && Object.keys(validationErrors).length === 0;
  };

  useEffect(() => {
    if (open) {
      validateForm(); // Trigger validation when modal opens
    }
  }, [open, validateForm]);

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center">
            <AddIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Create New Entity</Typography>
          </Box>
          {createEntity.loading && (
            <Box display="flex" alignItems="center">
              <CircularProgress size={20} sx={{ mr: 1 }} />
              <Typography variant="body2" color="text.secondary">
                Creating...
              </Typography>
            </Box>
          )}
        </Box>
        <Typography variant="body2" color="text.secondary">
          Add a new investing entity (person or company)
        </Typography>
      </DialogTitle>
      
      <DialogContent sx={{ pb: 2 }}>
        {/* Success State */}
        {success && (
          <Box sx={{ mb: 2, p: 2, bgcolor: 'success.light', borderRadius: 1, display: 'flex', alignItems: 'center' }}>
            <CheckCircleIcon sx={{ mr: 1, color: 'success.main' }} />
            <Box>
              <Typography variant="body1" fontWeight="medium" color="success.main">
                Entity created successfully!
              </Typography>
              <Typography variant="body2" color="success.main">
                Redirecting to fund creation...
              </Typography>
            </Box>
          </Box>
        )}

        {/* Error State */}
        {error && (
          <ErrorDisplay
            error={error}
            canRetry={error.retryable}
            onRetry={() => createEntity.mutate(formData)}
            onDismiss={clearError}
            variant="inline"
          />
        )}
        
        <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
            Entity Details
          </Typography>
          
          <Box display="flex" flexDirection="column" gap={3}>
            {/* Entity Name */}
            <TextField
              fullWidth
              label="Entity Name *"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              error={!!validationErrors.name}
              helperText={validationErrors.name || "Enter the entity name (2-255 characters)"}
              required
            />

            {/* Tax Jurisdiction */}
            <FormControl fullWidth>
              <InputLabel>Tax Jurisdiction</InputLabel>
              <Select
                value={formData.tax_jurisdiction}
                onChange={(e) => handleInputChange('tax_jurisdiction', e.target.value)}
                label="Tax Jurisdiction"
              >
                <MenuItem value="AU">Australia (AU)</MenuItem>
                <MenuItem value="US">United States (US)</MenuItem>
                <MenuItem value="UK">United Kingdom (UK)</MenuItem>
                <MenuItem value="CA">Canada (CA)</MenuItem>
              </Select>
            </FormControl>

            {/* Description */}
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              error={!!validationErrors.description}
              helperText={validationErrors.description || "Optional entity description (max 1000 characters)"}
            />
          </Box>
        </Paper>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button 
          onClick={handleClose} 
          disabled={createEntity.loading}
          variant="outlined"
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={createEntity.loading || !isFormValid()}
          startIcon={createEntity.loading ? <CircularProgress size={20} /> : <AddIcon />}
          sx={{ minWidth: 120 }}
        >
          {createEntity.loading ? 'Creating...' : 'Create Entity'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateEntityModal; 