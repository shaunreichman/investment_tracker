import React, { useEffect } from 'react';
import {
  TextField,
  Box,
  Typography
} from '@mui/material';
import { useCreateCompany } from '../hooks/useCompaniesold';
import { useErrorHandler } from '../hooks/useErrorHandlerold';
import { SuccessBanner } from './ui/SuccessBanner';
import { FormContainer } from './ui/FormContainer';
import { FormField } from './ui/FormField';
import { useUnifiedForm } from '../hooks/formsold/useUnifiedFormold';
import { createValidator, validationRules } from '../utils/validators';

interface CreateCompanyModalProps {
  open: boolean;
  onClose: () => void;
  onCompanyCreated: (company: { id: number; name: string }) => void;
}

// Form data interface
interface CompanyFormData {
  name: string;
  description: string;
  website: string;
  contact_email: string;
  contact_phone: string;
}

// Initial form values
const initialFormValues: CompanyFormData = {
  name: '',
  description: '',
  website: '',
  contact_email: '',
  contact_phone: ''
};

// Validation rules
const validators = {
  name: createValidator(
    validationRules.required('Company name'),
    (value: string) => {
      if (value.trim().length < 2) return 'Company name must be at least 2 characters';
      if (value.trim().length > 255) return 'Company name must be less than 255 characters';
      if (!/^[a-zA-Z0-9\s\-_()&.]+$/.test(value.trim())) {
        return 'Company name can only contain letters, numbers, spaces, hyphens, underscores, parentheses, ampersands, and periods';
      }
      return undefined;
    }
  ),
  description: (value: string) => {
    if (value && value.trim().length > 1000) {
      return 'Description must be less than 1000 characters';
    }
    return undefined;
  },
  website: (value: string) => {
    if (value && value.trim() !== '') {
      const urlPattern = /^https?:\/\/.+/;
      if (!urlPattern.test(value.trim())) {
        return 'Website must be a valid URL starting with http:// or https://';
      }
    }
    return undefined;
  },
  contact_email: (value: string) => {
    if (value && value.trim() !== '') {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailPattern.test(value.trim())) {
        return 'Please enter a valid email address';
      }
    }
    return undefined;
  },
  contact_phone: (value: string) => {
    if (value && value.trim() !== '') {
      const phonePattern = /^[+0-9()\s-]+$/;
      if (!phonePattern.test(value.trim())) {
        return 'Please enter a valid phone number';
      }
    }
    return undefined;
  }
};

const CreateCompanyModal: React.FC<CreateCompanyModalProps> = ({
  open,
  onClose,
  onCompanyCreated
}) => {
  // Centralized API hook
  const createCompany = useCreateCompany();

  // Centralized error handler
  const { error, setError, clearError } = useErrorHandler();

  // Unified form management
  const {
    values: formData,
    errors: validationErrors,
    touched,
    isDirty,
    isValid,
    isSubmitting,
    setFieldValue,
    handleSubmit,
    reset,
    clearErrors
  } = useUnifiedForm<CompanyFormData>({
    initialValues: initialFormValues,
    validators,
    onSubmit: async (values) => {
      const payload = {
        name: values.name.trim(),
        description: values.description.trim() || '',
        website: values.website.trim() || '',
        contact_email: values.contact_email.trim() || '',
        contact_phone: values.contact_phone.trim() || ''
      };
      await createCompany.mutate(payload);
    },
    onSuccess: () => {
      // Success will be handled by useEffect watching createCompany.data
    },
    onError: (error) => {
      setError(error);
    }
  });

  // Handle success flow when company is created
  useEffect(() => {
    if (createCompany.data) {
      onCompanyCreated({
        id: createCompany.data.id,
        name: createCompany.data.name
      });
      onClose();
      reset();
      clearErrors();
    }
  }, [createCompany.data, onCompanyCreated, onClose, reset, clearErrors]);

  // Handle errors from the API
  useEffect(() => {
    if (createCompany.error) {
      setError(createCompany.error);
    }
  }, [createCompany.error, setError]);

  // Reset form when modal opens
  useEffect(() => {
    if (open) {
      reset();
      clearErrors();
    }
  }, [open, reset, clearErrors]);

  // Handle form submission
  const handleFormSubmit = () => {
    clearError();
    handleSubmit();
  };

  // Handle modal close
  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
      clearError();
      reset();
      clearErrors();
    }
  };

  return (
    <FormContainer
      open={open}
      title="Create New Company"
      subtitle="Enter the details for the new company"
      onClose={handleClose}
      onSubmit={handleFormSubmit}
      isSubmitting={isSubmitting}
      isValid={isValid}
      isDirty={isDirty}
      showCloseConfirmation={true}
    >
      {/* Success Banner */}
      {createCompany.data && (
        <SuccessBanner 
          title="Company created successfully!" 
          subtitle={`Company ${createCompany.data.name} added to the Investment Tracker!`}
        />
      )}

      {/* Error Display */}
      {error && (
        <Box sx={{ mb: 2 }}>
          <Typography color="error" variant="body2">
            {error.userMessage || error.message || 'An error occurred'}
          </Typography>
        </Box>
      )}

      {/* Form Content */}
      <Box component="form" noValidate autoComplete="off">
        <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr' }} gap={2}>
          {/* Company Name */}
          <FormField
            label="Company Name"
            required
            error={validationErrors.name || undefined}
            touched={touched.name}
            showErrorOnlyWhenTouched={true}
          >
            <TextField
              fullWidth
              value={formData.name}
              onChange={(e) => setFieldValue('name', e.target.value)}
              placeholder="Enter company name"
              disabled={isSubmitting}
              error={!!validationErrors.name}
              size="medium"
            />
          </FormField>

          {/* Website */}
          <FormField
            label="Website"
            helperText="Company website URL (optional)"
            error={validationErrors.website || undefined}
            touched={touched.website}
            showErrorOnlyWhenTouched={true}
          >
            <TextField
              fullWidth
              value={formData.website}
              onChange={(e) => setFieldValue('website', e.target.value)}
              placeholder="https://example.com"
              disabled={isSubmitting}
              error={!!validationErrors.website}
              size="medium"
            />
          </FormField>

          {/* Contact Email */}
          <FormField
            label="Contact Email"
            helperText="Primary contact email (optional)"
            error={validationErrors.contact_email || undefined}
            touched={touched.contact_email}
            showErrorOnlyWhenTouched={true}
          >
            <TextField
              fullWidth
              type="email"
              value={formData.contact_email}
              onChange={(e) => setFieldValue('contact_email', e.target.value)}
              placeholder="contact@company.com"
              disabled={isSubmitting}
              error={!!validationErrors.contact_email}
              size="medium"
            />
          </FormField>

          {/* Contact Phone */}
          <FormField
            label="Contact Phone"
            helperText="Primary contact phone (optional)"
            error={validationErrors.contact_phone || undefined}
            touched={touched.contact_phone}
            showErrorOnlyWhenTouched={true}
          >
            <TextField
              fullWidth
              value={formData.contact_phone}
              onChange={(e) => setFieldValue('contact_phone', e.target.value)}
              placeholder="+1 (555) 123-4567"
              disabled={isSubmitting}
              error={!!validationErrors.contact_phone}
              size="medium"
            />
          </FormField>

          {/* Description */}
          <Box sx={{ gridColumn: '1 / -1' }}>
            <FormField
              label="Description"
              helperText="Company description and investment focus (max 1000 characters)"
              error={validationErrors.description || undefined}
              touched={touched.description}
              showErrorOnlyWhenTouched={true}
            >
              <TextField
                fullWidth
                multiline
                minRows={3}
                maxRows={6}
                value={formData.description}
                onChange={(e) => setFieldValue('description', e.target.value)}
                placeholder="Describe the company's investment strategy and focus areas"
                disabled={isSubmitting}
                error={!!validationErrors.description}
                size="medium"
              />
            </FormField>
          </Box>
        </Box>
      </Box>
    </FormContainer>
  );
};

export default CreateCompanyModal; 