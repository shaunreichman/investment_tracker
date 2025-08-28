import React, { useEffect } from 'react';
import {
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography
} from '@mui/material';
import { useCreateEntity } from '../hooks/useEntities';
import { useErrorHandler } from '../hooks/useErrorHandler';
import { SuccessBanner } from './ui/SuccessBanner';
import { FormContainer } from './ui/FormContainer';
import { FormField } from './ui/FormField';
import { useUnifiedForm } from '../hooks/forms/useUnifiedForm';
import { createValidator, validationRules } from '../utils/validators';

interface CreateEntityModalProps {
  open: boolean;
  onClose: () => void;
  onEntityCreated: (entity: { id: number; name: string }) => void;
}

// Form data interface
interface EntityFormData {
  name: string;
  description: string;
  tax_jurisdiction: string;
}

// Initial form values
const initialFormValues: EntityFormData = {
  name: '',
  description: '',
  tax_jurisdiction: 'AU'
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
        description: values.description.trim() || '',
        tax_jurisdiction: values.tax_jurisdiction
      };
      
      await createEntity.mutate(payload);
    },
    onSuccess: () => {
      // Success will be handled by useEffect watching createEntity.data
    },
    onError: setError
  });

  // Handle success flow when entity is created
  useEffect(() => {
    if (createEntity.data) {
      onEntityCreated({
        id: createEntity.data.id,
        name: createEntity.data.name
      });
      onClose();
      reset();
      clearErrors();
    }
  }, [createEntity.data, onEntityCreated, onClose, reset, clearErrors]);

  // Handle errors from the API
  useEffect(() => {
    if (createEntity.error) {
      setError(createEntity.error);
    }
  }, [createEntity.error, setError]);

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
       {createEntity.data && (
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
                 <MenuItem value="AU">Australia</MenuItem>
                 <MenuItem value="US">United States</MenuItem>
                 <MenuItem value="UK">United Kingdom</MenuItem>
                 <MenuItem value="CA">Canada</MenuItem>
                 <MenuItem value="NZ">New Zealand</MenuItem>
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