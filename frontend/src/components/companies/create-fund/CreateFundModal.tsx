import React, { useState, useEffect, useCallback } from 'react';
import { Box, Typography, Paper, Button } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import CreateEntityModal from '../../CreateEntityModal';
import { useEntities } from '../../../hooks/useEntities';
import { useCreateFund } from '../../../hooks/useFunds';
import { FundType } from '../../../types/api';
import { fundValidators, validationRules } from '../../../utils/validators';
import TemplateSelectionSection from './TemplateSelectionSection';
import FundFormSection from './FundFormSection';
import { FUND_TEMPLATES, FundTemplate } from './templates';
import { LoadingSpinner } from '../../ui/LoadingSpinner';
import { SuccessBanner } from '../../ui/SuccessBanner';
import { FormContainer } from '../../ui/FormContainer';
import { useUnifiedForm } from '../../../hooks/forms/useUnifiedForm';
import { createValidator } from '../../../utils/validators';

// Form data interface
interface FundFormData {
  entity_id: string;
  name: string;
  fund_type: string;
  tracking_type: string;
  currency: string;
  commitment_amount: string;
  expected_irr: string;
  expected_duration_months: string;
  description: string;
}

// Initial form values
const initialFormValues: FundFormData = {
  entity_id: '',
  name: '',
  fund_type: '',
  tracking_type: '',
  currency: 'AUD',
  commitment_amount: '',
  expected_irr: '',
  expected_duration_months: '',
  description: ''
};

// Validation rules
const validators = {
  entity_id: validationRules.required('Entity'),
  name: fundValidators.name,
  fund_type: fundValidators.fundType,
  tracking_type: validationRules.required('Tracking type'),
  currency: validationRules.required('Currency'),
  commitment_amount: fundValidators.commitmentAmount,
  expected_irr: fundValidators.expectedIrr,
  expected_duration_months: fundValidators.expectedDuration,
  description: fundValidators.description,
};

interface CreateFundModalProps {
  open: boolean;
  onClose: () => void;
  onFundCreated: () => void;
  companyId: number;
  companyName: string;
}

const CreateFundModal: React.FC<CreateFundModalProps> = ({
  open,
  onClose,
  onFundCreated,
  companyId,
  companyName
}) => {
  const [showEntityModal, setShowEntityModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<FundTemplate | null>(null);
  const [showTemplateSelection, setShowTemplateSelection] = useState(true);

  // Centralized API hooks
  const { data: entities, loading, error: entitiesError } = useEntities({ refetchOnWindowFocus: true });
  const { mutate: createFund, loading: isSubmitting, error: submitError, data: createdFund } = useCreateFund();

  // Unified form management
  const {
    values: formData,
    errors: validationErrors,
    touched,
    isDirty,
    isValid,
    isSubmitting: formIsSubmitting,
    setFieldValue,
    handleSubmit,
    reset,
    clearErrors,
    setFieldError
  } = useUnifiedForm<FundFormData>({
    initialValues: initialFormValues,
    validators,
    onSubmit: async (values) => {
      const fundData = {
        investment_company_id: companyId,
        entity_id: parseInt(values.entity_id),
        name: values.name.trim(),
        fund_type: values.fund_type,
        tracking_type: values.tracking_type === 'nav_based' ? FundType.NAV_BASED : FundType.COST_BASED,
        currency: values.currency,
        ...(values.commitment_amount && { commitment_amount: parseFloat(values.commitment_amount) }),
        ...(values.expected_irr && { expected_irr: parseFloat(values.expected_irr) }),
        ...(values.expected_duration_months && { expected_duration_months: parseInt(values.expected_duration_months) }),
        ...(values.description && { description: values.description.trim() })
      };
      
      await createFund(fundData);
    },
    onSuccess: () => {
      // Success will be handled by useEffect watching createdFund
    },
    onError: (error) => {
      console.error('Form submission error:', error);
    }
  });

  // Handle success flow when fund is created
  useEffect(() => {
    if (createdFund) {
      onFundCreated();
      onClose();
      reset();
      clearErrors();
      setSelectedTemplate(null);
      setShowTemplateSelection(true);
    }
  }, [createdFund, onFundCreated, onClose, reset, clearErrors]);

  // Reset form when modal opens
  useEffect(() => {
    if (open) {
      reset();
      clearErrors();
      setSelectedTemplate(null);
      setShowTemplateSelection(true);
    }
  }, [open, reset, clearErrors]);

  // Apply template to form data
  const applyTemplate = (template: FundTemplate) => {
    const templateValues = {
      entity_id: '',
      name: '',
      fund_type: template.fund_type,
      tracking_type: template.tracking_type,
      currency: template.currency,
      commitment_amount: template.commitment_amount?.toString() || '',
      expected_irr: template.expected_irr?.toString() || '',
      expected_duration_months: template.expected_duration_months?.toString() || '',
      description: template.description_template
    };

    // Update form values
    Object.entries(templateValues).forEach(([key, value]) => {
      setFieldValue(key as keyof FundFormData, value);
    });

    setSelectedTemplate(template);
    setShowTemplateSelection(false);

    // Clear validation errors for fields filled by template
    const errorsToClear: Partial<Record<keyof FundFormData, string | undefined>> = {};
    Object.keys(templateValues).forEach(key => {
      if (templateValues[key as keyof FundFormData]) {
        errorsToClear[key as keyof FundFormData] = undefined;
      }
    });
    
    // Clear the errors
    Object.entries(errorsToClear).forEach(([key, value]) => {
      setFieldError(key as keyof FundFormData, value);
    });
  };

  // Handle input change
  const handleInputChange = (field: string, value: string) => {
    setFieldValue(field as keyof FundFormData, value);
  };

  // Handle form submission
  const handleFormSubmit = () => {
    if (showTemplateSelection) return;
    handleSubmit();
  };

  // Handle modal close
  const handleClose = () => {
    if (!isSubmitting && !formIsSubmitting) {
      onClose();
      reset();
      clearErrors();
      setSelectedTemplate(null);
      setShowTemplateSelection(true);
    }
  };

  // Handle entity creation
  const handleEntityCreated = (entity: { id: number; name: string }) => {
    setFieldValue('entity_id', entity.id.toString());
    setFieldError('entity_id', undefined);
  };

  // Form validation status
  const isFormValid = () => {
    const requiredFields = ['entity_id', 'name', 'fund_type', 'tracking_type'];
    const requiredFieldsValid = requiredFields.every(field => {
      const value = formData[field as keyof FundFormData];
      return value && value.toString().trim() !== '';
    });
    return requiredFieldsValid && isValid;
  };

  // Form progress calculation
  const getFormProgress = () => {
    const requiredFields = ['entity_id', 'name', 'fund_type', 'tracking_type'];
    const completedFields = requiredFields.filter(field => {
      const value = formData[field as keyof FundFormData];
      return value && value.toString().trim() !== '';
    });
    return (completedFields.length / requiredFields.length) * 100;
  };

  // Validation status
  const getValidationStatus = () => {
    const requiredFields = ['entity_id', 'name', 'fund_type', 'tracking_type'];
    const missingFields = requiredFields.filter(field => {
      const value = formData[field as keyof FundFormData];
      return !value || value.toString().trim() === '';
    });
    const errorFields = Object.keys(validationErrors).filter(key => validationErrors[key as keyof FundFormData]);
    return {
      missingFields,
      errorFields,
      hasErrors: errorFields.length > 0,
      isComplete: missingFields.length === 0 && errorFields.length === 0
    };
  };

  return (
    <FormContainer
      open={open}
      title="Create New Fund"
      subtitle={`Adding fund to ${companyName}`}
      onClose={handleClose}
      onSubmit={handleFormSubmit}
      isSubmitting={isSubmitting || formIsSubmitting}
      isValid={!showTemplateSelection ? isFormValid() : true}
      isDirty={isDirty}
      showCloseConfirmation={true}
      maxWidth="md"
      fullWidth={true}
      actions={
        <>
          {!showTemplateSelection && selectedTemplate && (
            <Button 
              onClick={() => setShowTemplateSelection(true)} 
              variant="outlined" 
              disabled={isSubmitting || formIsSubmitting} 
              startIcon={<AddIcon />}
            >
              Back to Templates
            </Button>
          )}
        </>
      }
    >
      {/* Progress Indicator */}
      <Box sx={{ mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="body2" color="text.secondary">
            Form Progress
          </Typography>
          <Typography variant="body2" color="primary.main" fontWeight="medium">
            {Math.round(getFormProgress())}% Complete
          </Typography>
        </Box>
        <Box sx={{ width: '100%', bgcolor: 'background.default', borderRadius: 1, height: 8 }}>
          <Box
            sx={{
              width: `${getFormProgress()}%`,
              bgcolor: 'primary.main',
              height: 8,
              borderRadius: 1,
              transition: 'width 0.3s ease'
            }}
          />
        </Box>
        {!showTemplateSelection && (
          <Box sx={{ mt: 1 }}>
            {(() => {
              const status = getValidationStatus();
              if (status.missingFields.length > 0) {
                return (
                  <Typography variant="caption" color="warning.main">
                    Missing required fields: {status.missingFields.join(', ')}
                  </Typography>
                );
              } else if (status.hasErrors) {
                return (
                  <Typography variant="caption" color="error.main">
                    Please fix validation errors
                  </Typography>
                );
              } else {
                return (
                  <Typography variant="caption" color="success.main">
                    ✓ All required fields completed
                  </Typography>
                );
              }
            })()}
          </Box>
        )}
      </Box>

      {/* Success State */}
      {createdFund && (
        <SuccessBanner 
          title="Fund created successfully!" 
          subtitle="Redirecting to fund details..." 
        />
      )}

      {/* Error State */}
      {(submitError || entitiesError) && (
        <Box sx={{ mb: 2 }}>
          <Typography color="error" variant="body2">
            {submitError?.userMessage || submitError?.message || 
             entitiesError?.userMessage || entitiesError?.message || 
             'An error occurred'}
          </Typography>
        </Box>
      )}

      {loading ? (
        <Box p={4}>
          <LoadingSpinner label="Loading entities..." />
        </Box>
      ) : (
        <Paper elevation={0} sx={{ p: 3, bgcolor: 'background.paper', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
            Fund Details
          </Typography>

          {showTemplateSelection ? (
            <TemplateSelectionSection templates={FUND_TEMPLATES} onSelect={applyTemplate} />
          ) : (
            <Box>
              {selectedTemplate && (
                <Box sx={{ mb: 3, p: 2, bgcolor: 'primary.light', borderRadius: 1 }}>
                  <Box display="flex" alignItems="center" gap={2}>
                    {selectedTemplate.icon}
                    <Typography variant="h6">Using Template: {selectedTemplate.name}</Typography>
                    <Typography variant="caption" sx={{ bgcolor: 'primary.main', color: 'white', px: 1, py: 0.5, borderRadius: 1, fontSize: '0.75rem' }}>
                      {selectedTemplate.tracking_type}
                    </Typography>
                    <Typography variant="caption" sx={{ bgcolor: 'divider', color: 'text.secondary', px: 1, py: 0.5, borderRadius: 1, fontSize: '0.75rem' }}>
                      {selectedTemplate.currency}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {selectedTemplate.description}
                  </Typography>
                </Box>
              )}

                             <FundFormSection
                 formData={formData}
                 validationErrors={validationErrors as any}
                 entities={entities || []}
                 onInputChange={handleInputChange}
                 onCreateEntity={() => setShowEntityModal(true)}
                 trackingTypeLocked={true}
               />
            </Box>
          )}
        </Paper>
      )}

      {/* Entity Creation Modal */}
      <CreateEntityModal 
        open={showEntityModal} 
        onClose={() => setShowEntityModal(false)} 
        onEntityCreated={handleEntityCreated} 
      />
    </FormContainer>
  );
};

export default CreateFundModal;


