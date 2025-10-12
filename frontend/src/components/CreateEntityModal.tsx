import React, { useEffect, useCallback, useRef } from 'react';
import {
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography
} from '@mui/material';
import { useCreateEntity } from '../hooks/useEntitiesold';
import { useErrorHandler } from '../hooks/useErrorHandlerold';
import { SuccessBanner } from './ui/SuccessBanner';
import { FormContainer } from './ui/FormContainer';
import { FormField } from './ui/FormField';
import { useUnifiedForm } from '../hooks/formsold/useUnifiedFormold';
import { createValidator, validationRules } from '../utils/validators';
import { EntityType } from '../types/enums/entity.enums';
import { Country } from '../types/enums/shared.enums';
import { ENTITY_TYPE_LABELS, COUNTRY_LABELS } from '../utils/labels';

interface CreateEntityModalProps {
  open: boolean;
  onClose: () => void;
  onEntityCreated: (entity: { id: number; name: string }) => void;
}

// Form data interface
interface EntityFormData {
  name: string;
  description: string;
  entity_type: EntityType;
  tax_jurisdiction: Country;
}

// Initial form values
const initialFormValues: EntityFormData = {
  name: '',
  description: '',
  entity_type: EntityType.PERSON,
  tax_jurisdiction: Country.AU
};

// Validation rules
const validators = {
  name: createValidator(
    validationRules.required('Entity name'),
    (value: string) => {
      if (value.trim().length < 2) return 'Entity name must be at least 2 characters';
      if (value.trim().length > 255) return 'Entity name must be less than 255 characters';
      if (!/^[a-zA-Z0-9\s\-_()]+$/.test(value.trim())) {
        return 'Entity name can only contain letters, numbers, spaces, hyphens, underscores, and parentheses';
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
  entity_type: validationRules.required('Entity type'),
  tax_jurisdiction: validationRules.required('Tax jurisdiction')
};

const CreateEntityModal: React.FC<CreateEntityModalProps> = ({
  open,
  onClose,
  onEntityCreated
}) => {
  // Centralized API hook
  const createEntity = useCreateEntity();

  // Centralized error handler
  const { error, setError, clearError } = useErrorHandler();

  // ENTERPRISE-GRADE SOLUTION: Track entity creation state to prevent re-triggering
  const entityCreatedRef = useRef<{ id: number; name: string } | null>(null);

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
  } = useUnifiedForm<EntityFormData>({
    initialValues: initialFormValues,
    validators,
    onSubmit: async (values) => {
      const payload = {
        name: values.name.trim(),
        description: values.description.trim(),
        entity_type: values.entity_type,
        tax_jurisdiction: values.tax_jurisdiction
      };
      
      await createEntity.mutate(payload);
    },
    onSuccess: () => {
      // Success will be handled by useEffect watching createEntity.data
    },
    onError: setError
  });

  // ENTERPRISE-GRADE SOLUTION: Proper form state cleanup and isolation
  const handleEntityCreated = useCallback((entity: { id: number; name: string }) => {
    // 1. Store the created entity to prevent re-triggering
    entityCreatedRef.current = entity;
    
    // 2. Call the parent callback first
    onEntityCreated(entity);
    
    // 3. Clear any API errors
    clearError();
    
    // 4. Reset form state completely
    reset();
    clearErrors();
    
    // 5. Close modal immediately
    onClose();
  }, [onEntityCreated, clearError, reset, clearErrors, onClose]);

  // Handle success flow when entity is created
  useEffect(() => {
    if (createEntity.data && !entityCreatedRef.current) {
      handleEntityCreated({
        id: createEntity.data.id,
        name: createEntity.data.name
      });
    }
  }, [createEntity.data, handleEntityCreated]);

  // Handle errors from the API
  useEffect(() => {
    if (createEntity.error) {
      setError(createEntity.error);
    }
  }, [createEntity.error, setError]);

  // ENTERPRISE-GRADE SOLUTION: Proper form initialization when modal opens
  useEffect(() => {
    if (open) {
      // Clear the entity creation tracking when modal opens
      entityCreatedRef.current = null;
      
      // Ensure complete form state reset when modal opens
      // Use setTimeout to avoid state conflicts during render
      setTimeout(() => {
        reset();
        clearErrors();
        clearError();
      }, 0);
    }
  }, [open, reset, clearErrors, clearError]);

  // Handle form submission
  const handleFormSubmit = () => {
    clearError();
    handleSubmit();
  };

  // ENTERPRISE-GRADE SOLUTION: Robust modal close handling
  const handleClose = useCallback(() => {
    if (!isSubmitting) {
      // Clear all state before closing
      clearError();
      reset();
      clearErrors();
      onClose();
    }
  }, [isSubmitting, clearError, reset, clearErrors, onClose]);

  return (
    <FormContainer
      open={open}
      title="Create New Entity"
      subtitle="Enter the details for the new entity"
      onClose={handleClose}
      onSubmit={handleFormSubmit}
      isSubmitting={isSubmitting}
      isValid={isValid}
      isDirty={isDirty}
      showCloseConfirmation={true}
    >
      {/* Success Banner */}
      {createEntity.data && entityCreatedRef.current && (
        <SuccessBanner 
          title="Entity created successfully!" 
          subtitle={`Entity ${createEntity.data.name} added to the Investment Tracker!`}
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
          {/* Entity Name */}
          <FormField
            label="Entity Name"
            required
            error={validationErrors.name || undefined}
            touched={touched.name}
            showErrorOnlyWhenTouched={true}
          >
            <TextField
              fullWidth
              value={formData.name}
              onChange={(e) => setFieldValue('name', e.target.value)}
              placeholder="Enter entity name"
              disabled={isSubmitting}
              error={!!validationErrors.name}
              size="medium"
            />
          </FormField>

          {/* Entity Type */}
          <FormField
            label="Entity Type"
            required
            error={validationErrors.entity_type || undefined}
            touched={touched.entity_type}
            showErrorOnlyWhenTouched={true}
          >
            <FormControl fullWidth error={!!validationErrors.entity_type}>
              <InputLabel>Entity Type</InputLabel>
              <Select
                value={formData.entity_type}
                onChange={(e) => setFieldValue('entity_type', e.target.value)}
                label="Entity Type"
                disabled={isSubmitting}
              >
                {Object.values(EntityType).map((type) => (
                  <MenuItem key={type} value={type}>
                    {ENTITY_TYPE_LABELS[type]}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </FormField>

          {/* Tax Jurisdiction */}
          <FormField
            label="Tax Jurisdiction"
            required
            error={validationErrors.tax_jurisdiction || undefined}
            touched={touched.tax_jurisdiction}
            showErrorOnlyWhenTouched={true}
          >
            <FormControl fullWidth error={!!validationErrors.tax_jurisdiction}>
              <InputLabel>Tax Jurisdiction</InputLabel>
              <Select
                value={formData.tax_jurisdiction}
                onChange={(e) => setFieldValue('tax_jurisdiction', e.target.value)}
                label="Tax Jurisdiction"
                disabled={isSubmitting}
              >
                {Object.values(Country).map((country) => (
                  <MenuItem key={country} value={country}>
                    {COUNTRY_LABELS[country]}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </FormField>

          {/* Description */}
          <Box sx={{ gridColumn: '1 / -1' }}>
            <FormField
              label="Description"
              helperText="Optional description for the entity (max 1000 characters)"
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
                placeholder="Enter entity description (optional)"
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

export default CreateEntityModal; 