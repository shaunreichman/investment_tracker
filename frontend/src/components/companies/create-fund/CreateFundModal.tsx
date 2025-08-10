import React, { useState, useEffect, useCallback } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, CircularProgress, Typography, Paper } from '@mui/material';
import { ErrorDisplay } from '../../ErrorDisplay';
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
import { useFormState } from '../../../hooks/forms/useFormState';
import { useFormValidation } from '../../../hooks/forms/useFormValidation';

// Form fields - constant values that don't change
const initialFormValues = {
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

interface CreateFundModalProps {
  open: boolean;
  onClose: () => void;
  onFundCreated: () => void;
  companyId: number;
  companyName: string;
}

//

// Fund type templates with predefined values

const CreateFundModal: React.FC<CreateFundModalProps> = ({
  open,
  onClose,
  onFundCreated,
  companyId,
  companyName
}) => {
  const [success, setSuccess] = useState(false);
  const [showEntityModal, setShowEntityModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<FundTemplate | null>(null);
  const [showTemplateSelection, setShowTemplateSelection] = useState(true);


  const { values: formData, setFieldValue, setValues, reset } = useFormState(initialFormValues);

  // Validation using centralized validators
  const { errors: validationErrors, validateField, validateAll, setErrors } = useFormValidation<typeof initialFormValues>({
    entity_id: validationRules.required('Entity'),
    name: fundValidators.name,
    fund_type: fundValidators.fundType,
    tracking_type: validationRules.required('Tracking type'),
    // currency: optional, no validator
    commitment_amount: fundValidators.commitmentAmount,
    expected_irr: fundValidators.expectedIrr,
    expected_duration_months: fundValidators.expectedDuration,
    description: fundValidators.description,
  });

  // Centralized API hooks
  const { data: entities, loading, error: entitiesError } = useEntities({ refetchOnWindowFocus: true });
  const { mutate: createFund, loading: isSubmitting, error: submitError, data: createdFund } = useCreateFund();

  // Handle success flow when fund is created
  useEffect(() => {
    if (createdFund) {
      setSuccess(true);
      const timer = setTimeout(() => {
        onFundCreated();
        onClose();
        setSuccess(false);
        reset(initialFormValues);
        setErrors({});
      }, 2000);
      
      return () => clearTimeout(timer);
    }
  }, [createdFund, onFundCreated, onClose, reset, setErrors]);

  // Reset form when modal opens
  useEffect(() => {
    if (open) {
      reset(initialFormValues);
      setSelectedTemplate(null);
      setShowTemplateSelection(true);
      setErrors({});
      setSuccess(false);
    }
  }, [open, reset, setErrors]);

  // Apply template to form data
  const applyTemplate = (template: FundTemplate) => {
    setValues({
      entity_id: '',
      name: '',
      fund_type: template.fund_type,
      tracking_type: template.tracking_type,
      currency: template.currency,
      commitment_amount: template.commitment_amount?.toString() || '',
      expected_irr: template.expected_irr?.toString() || '',
      expected_duration_months: template.expected_duration_months?.toString() || '',
      description: template.description_template
    });
    setSelectedTemplate(template);
    setShowTemplateSelection(false);

    // Clear validation errors only for fields that are filled by the template
    setErrors({
      tracking_type: undefined,
      currency: undefined,
      fund_type: template.fund_type ? undefined : validationErrors.fund_type,
      commitment_amount: template.commitment_amount ? undefined : validationErrors.commitment_amount,
      expected_irr: template.expected_irr ? undefined : validationErrors.expected_irr,
      expected_duration_months: template.expected_duration_months ? undefined : validationErrors.expected_duration_months,
      description: template.description_template ? undefined : validationErrors.description
    });
  };

  const validateForm = useCallback((): boolean => {
    // Run all validators
    const allValid = validateAll(formData as typeof initialFormValues);
    // Preserve required field semantics for submit enablement
    const requiredFieldsValid = Boolean(
      formData.entity_id && formData.name.trim() && formData.fund_type && formData.tracking_type
    );
    return allValid && requiredFieldsValid;
  }, [formData, validateAll]);

  useEffect(() => {
    if (open) {
      validateForm();
    }
  }, [open, validateForm]);

  // Remove the problematic useEffect that depends on formData
  // This was causing infinite loops
  // useEffect(() => {
  //   if (open && !showTemplateSelection) {
  //     validateForm();
  //   }
  // }, [formData, open, showTemplateSelection, validateForm]);

  const handleInputChange = (field: string, value: string) => {
    setFieldValue(field as keyof typeof initialFormValues, value);
    validateField(field as keyof typeof initialFormValues, value);
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;
    
    const fundData = {
      investment_company_id: companyId,
      entity_id: parseInt(formData.entity_id),
      name: formData.name.trim(),
      fund_type: formData.fund_type,
      tracking_type: formData.tracking_type === 'nav_based' ? FundType.NAV_BASED : FundType.COST_BASED,
      currency: formData.currency,
      commitment_amount: formData.commitment_amount ? parseFloat(formData.commitment_amount) : undefined,
      expected_irr: formData.expected_irr ? parseFloat(formData.expected_irr) : undefined,
      expected_duration_months: formData.expected_duration_months ? parseInt(formData.expected_duration_months) : undefined,
      description: formData.description.trim() || undefined
    };
    
    await createFund(fundData);
  };

  const handleClose = () => {
    if (!isSubmitting) { // Use isSubmitting from hook
      onClose();
      setSuccess(false);
      setErrors({});
      reset(initialFormValues);
      setSelectedTemplate(null);
      setShowTemplateSelection(true);
    }
  };

  const handleEntityCreated = (entity: { id: number; name: string }) => {
    setFieldValue('entity_id', entity.id.toString());
    setErrors({ entity_id: undefined });
  };

  const isFormValid = () => {
    const requiredFieldsValid = formData.entity_id && formData.name.trim() && formData.fund_type && formData.tracking_type;
    const noValidationErrors = Object.values(validationErrors).every(error => !error);
    return requiredFieldsValid && noValidationErrors;
  };

  const getFormProgress = () => {
    const requiredFields = ['entity_id', 'name', 'fund_type', 'tracking_type'];
    const completedFields = requiredFields.filter(field => {
      const value = (formData as any)[field];
      return value && value.toString().trim() !== '';
    });
    return (completedFields.length / requiredFields.length) * 100;
  };

  const getValidationStatus = () => {
    const requiredFields = ['entity_id', 'name', 'fund_type', 'tracking_type'];
    const missingFields = requiredFields.filter(field => {
      const value = (formData as any)[field];
      return !value || value.toString().trim() === '';
    });
    const errorFields = Object.keys(validationErrors).filter(key => (validationErrors as any)[key]);
    return {
      missingFields,
      errorFields,
      hasErrors: errorFields.length > 0,
      isComplete: missingFields.length === 0 && errorFields.length === 0
    };
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center">
            <AddIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Create New Fund</Typography>
          </Box>
          {isSubmitting && ( // Use isSubmitting from hook
            <Box display="flex" alignItems="center">
              <CircularProgress size={20} sx={{ mr: 1 }} />
              <Typography variant="body2" color="text.secondary">
                Creating...
              </Typography>
            </Box>
          )}
        </Box>
        <Typography variant="body2" color="text.secondary">
          Adding fund to <strong>{companyName}</strong>
        </Typography>
      </DialogTitle>

      <DialogContent sx={{ pb: 2 }}>
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
          <Box sx={{ width: '100%', bgcolor: 'grey.200', borderRadius: 1, height: 8 }}>
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
        {success && (
          <SuccessBanner title="Fund created successfully!" subtitle="Redirecting to fund details..." />
        )}

        {/* Error State */}
        {(submitError || entitiesError) && (
          <ErrorDisplay
            error={submitError || entitiesError}
            canRetry={(submitError || entitiesError)!.retryable}
            onRetry={() => handleSubmit()}
            onDismiss={() => {}}
            variant="inline"
          />
        )}

        {loading ? (
          <Box p={4}>
            <LoadingSpinner label="Loading entities..." />
          </Box>
        ) : (
          <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50', borderRadius: 2 }}>
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
                      <Typography variant="caption" sx={{ bgcolor: 'grey.300', px: 1, py: 0.5, borderRadius: 1, fontSize: '0.75rem' }}>
                        {selectedTemplate.currency}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {selectedTemplate.description}
                    </Typography>
                  </Box>
                )}

                <FundFormSection
                  formData={formData as any}
                  validationErrors={validationErrors as any}
                  entities={entities as any}
                  onInputChange={handleInputChange}
                  onCreateEntity={() => setShowEntityModal(true)}
                  trackingTypeLocked={true}
                />
              </Box>
            )}
          </Paper>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        {!showTemplateSelection && selectedTemplate && (
          <Button onClick={() => setShowTemplateSelection(true)} variant="outlined" disabled={isSubmitting} startIcon={<AddIcon />}>
            Back to Templates
          </Button>
        )}
        <Button onClick={handleClose} disabled={isSubmitting} variant="outlined">
          Cancel
        </Button>
        {!showTemplateSelection && (
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={isSubmitting || !isFormValid()}
            startIcon={isSubmitting ? <CircularProgress size={20} /> : <AddIcon />}
            sx={{ minWidth: 120 }}
            title={!isFormValid() ? 'Please fill in all required fields and fix any validation errors' : ''}
          >
            {isSubmitting ? 'Creating...' : 'Create Fund'}
          </Button>
        )}
      </DialogActions>

      {/* Entity Creation Modal */}
      <CreateEntityModal open={showEntityModal} onClose={() => setShowEntityModal(false)} onEntityCreated={handleEntityCreated} />
    </Dialog>
  );
};

export default CreateFundModal;


