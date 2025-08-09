import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  CircularProgress,
  Typography,
  Paper
} from '@mui/material';
import { ErrorDisplay } from './ErrorDisplay';
import { useErrorHandler } from '../hooks/useErrorHandler';
import { Add as AddIcon, CheckCircle as CheckCircleIcon, Business as BusinessIcon } from '@mui/icons-material';
import { useCreateInvestmentCompany } from '../hooks/useInvestmentCompanies';

interface CreateInvestmentCompanyModalProps {
  open: boolean;
  onClose: () => void;
  onCompanyCreated: (company: { id: number; name: string }) => void;
}

interface ValidationErrors {
  name?: string;
  description?: string;
  website?: string;
  contact_email?: string;
  contact_phone?: string;
}

const CreateInvestmentCompanyModal: React.FC<CreateInvestmentCompanyModalProps> = ({
  open,
  onClose,
  onCompanyCreated
}) => {
  const [success, setSuccess] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});

  // Form fields
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    website: '',
    contact_email: '',
    contact_phone: ''
  });

  // Centralized API hook
  const createInvestmentCompany = useCreateInvestmentCompany();

  // Centralized error handler
  const { error, setError, clearError } = useErrorHandler();

  // Handle errors and success from hooks
  useEffect(() => {
    if (createInvestmentCompany.error) {
      setError(createInvestmentCompany.error);
    }
  }, [createInvestmentCompany.error, setError]);

  useEffect(() => {
    if (createInvestmentCompany.data) {
      setSuccess(true);
      setTimeout(() => {
        onCompanyCreated({
          id: createInvestmentCompany.data!.id,
          name: createInvestmentCompany.data!.name
        });
        onClose();
        setSuccess(false);
        setFormData({
          name: '',
          description: '',
          website: '',
          contact_email: '',
          contact_phone: ''
        });
        setValidationErrors({});
      }, 2000);
    }
  }, [createInvestmentCompany.data, onCompanyCreated, onClose]);

  // Validation rules
  const validateField = useCallback((field: string, value: string): string | undefined => {
    switch (field) {
      case 'name':
        if (!value.trim()) return 'Company name is required';
        if (value.trim().length < 2) return 'Company name must be at least 2 characters';
        if (value.trim().length > 255) return 'Company name must be less than 255 characters';
        if (!/^[a-zA-Z0-9\s\-_()&.]+$/.test(value.trim())) {
          return 'Company name can only contain letters, numbers, spaces, hyphens, underscores, parentheses, ampersands, and periods';
        }
        break;
      
      case 'description':
        if (value && value.trim().length > 1000) {
          return 'Description must be less than 1000 characters';
        }
        break;
      
      case 'website':
        if (value && value.trim() !== '') {
          const urlPattern = /^https?:\/\/.+/;
          if (!urlPattern.test(value.trim())) {
            return 'Website must be a valid URL starting with http:// or https://';
          }
        }
        break;
      
      case 'contact_email':
        if (value && value.trim() !== '') {
          const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailPattern.test(value.trim())) {
            return 'Please enter a valid email address';
          }
        }
        break;
      
      case 'contact_phone':
        if (value && value.trim() !== '') {
          const phonePattern = /^[+0-9()\s-]+$/;
          if (!phonePattern.test(value.trim())) {
            return 'Please enter a valid phone number';
          }
        }
        break;
    }
    return undefined;
  }, []);

  const validateForm = useCallback((): boolean => {
    const errors: ValidationErrors = {};
    
    // Required fields
    if (!formData.name.trim()) {
      errors.name = 'Company name is required';
    }
    
    // Field-specific validation
    const nameError = validateField('name', formData.name);
    if (nameError) errors.name = nameError;
    
    const descriptionError = validateField('description', formData.description);
    if (descriptionError) errors.description = descriptionError;
    
    const websiteError = validateField('website', formData.website);
    if (websiteError) errors.website = websiteError;
    
    const emailError = validateField('contact_email', formData.contact_email);
    if (emailError) errors.contact_email = emailError;
    
    const phoneError = validateField('contact_phone', formData.contact_phone);
    if (phoneError) errors.contact_phone = phoneError;
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  }, [formData, validateField]);

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
      website: formData.website.trim() || '',
      contact_email: formData.contact_email.trim() || '',
      contact_phone: formData.contact_phone.trim() || ''
    };

    await createInvestmentCompany.mutate(payload);
  };

  const handleClose = () => {
    if (!createInvestmentCompany.loading) {
      onClose();
      clearError();
      setSuccess(false);
      setValidationErrors({});
      // Clear form data when closing
      setFormData({
        name: '',
        description: '',
        website: '',
        contact_email: '',
        contact_phone: ''
      });
    }
  };

  const isFormValid = () => {
    return formData.name.trim() && 
           Object.values(validationErrors).every(error => !error);
  };

  useEffect(() => {
    if (open) {
      validateForm(); // Trigger validation when modal opens
    }
  }, [open, validateForm]);

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center">
            <BusinessIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Create New Investment Company</Typography>
          </Box>
          {createInvestmentCompany.loading && (
            <Box display="flex" alignItems="center">
              <CircularProgress size={20} sx={{ mr: 1 }} />
              <Typography variant="body2" color="text.secondary">
                Creating...
              </Typography>
            </Box>
          )}
        </Box>
        <Typography variant="body2" color="text.secondary">
          Add a new investment company or fund manager
        </Typography>
      </DialogTitle>
      
      <DialogContent sx={{ pb: 2 }}>
        {/* Success State */}
        {success && (
          <Box sx={{ mb: 2, p: 2, bgcolor: 'success.light', borderRadius: 1, display: 'flex', alignItems: 'center' }}>
            <CheckCircleIcon sx={{ mr: 1, color: 'success.main' }} />
            <Box>
              <Typography variant="body1" fontWeight="medium" color="success.main">
                Investment company created successfully!
              </Typography>
              <Typography variant="body2" color="success.main">
                Redirecting to dashboard...
              </Typography>
            </Box>
          </Box>
        )}

        {/* Error State */}
        {error && (
          <ErrorDisplay
            error={error}
            canRetry={error.retryable}
            onRetry={() => createInvestmentCompany.mutate(formData)}
            onDismiss={clearError}
            variant="inline"
          />
        )}
        
        <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
            Company Details
          </Typography>
          
          <Box display="grid" gap={3} sx={{ gridTemplateColumns: '1fr 1fr' }}>
            {/* Company Name */}
            <TextField
              fullWidth
              label="Company Name *"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              error={!!validationErrors.name}
              helperText={validationErrors.name || "Enter the company name (2-255 characters)"}
              required
            />

            {/* Website */}
            <TextField
              fullWidth
              label="Website"
              value={formData.website}
              onChange={(e) => handleInputChange('website', e.target.value)}
              error={!!validationErrors.website}
              helperText={validationErrors.website || "Company website URL (optional)"}
              placeholder="https://example.com"
            />

            {/* Contact Email */}
            <TextField
              fullWidth
              label="Contact Email"
              type="email"
              value={formData.contact_email}
              onChange={(e) => handleInputChange('contact_email', e.target.value)}
              error={!!validationErrors.contact_email}
              helperText={validationErrors.contact_email || "Contact email address (optional)"}
              placeholder="contact@company.com"
            />

            {/* Contact Phone */}
            <TextField
              fullWidth
              label="Contact Phone"
              value={formData.contact_phone}
              onChange={(e) => handleInputChange('contact_phone', e.target.value)}
              error={!!validationErrors.contact_phone}
              helperText={validationErrors.contact_phone || "Contact phone number (optional)"}
              placeholder="+61 2 1234 5678"
            />

            {/* Description */}
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              error={!!validationErrors.description}
              helperText={validationErrors.description || "Company description (optional, max 1000 characters)"}
              sx={{ gridColumn: '1 / -1' }}
            />
          </Box>
        </Paper>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button 
          onClick={handleClose} 
          disabled={createInvestmentCompany.loading}
          variant="outlined"
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={createInvestmentCompany.loading || !isFormValid()}
          startIcon={createInvestmentCompany.loading ? <CircularProgress size={20} /> : <AddIcon />}
          sx={{ minWidth: 120 }}
        >
          {createInvestmentCompany.loading ? 'Creating...' : 'Create Company'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateInvestmentCompanyModal; 