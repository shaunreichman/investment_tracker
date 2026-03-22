import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Button, CircularProgress } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { FormProvider } from 'react-hook-form';
import CreateEntityModal from '../../CreateEntityModal';
import { useEntities } from '@/entity/hooks';
import { useCreateFund } from '@/fund/hooks';
import { FundTrackingType } from '@/fund/types';
import { Country, Currency } from '@/shared/types';
import TemplateSelectionSection from './TemplateSelectionSection';
import FundFormSection from './FundFormSection';
import { FUND_TEMPLATES, FundTemplate } from './templates';
import { LoadingSpinner, SuccessBanner } from '../../shared/feedback';
import { FormModal } from '../../shared/overlays';
import { useForm } from '@/shared/hooks/forms';
import { createFundSchema, type CreateFundFormData } from '@/fund/hooks/schemas';
import { transformCreateFundForm } from '@/fund/hooks/transformers';

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
  const { data: entities, loading, error: entitiesError } = useEntities(undefined, { refetchOnWindowFocus: true });
  const { mutate: createFund, loading: isSubmitting, error: submitError, data: createdFund } = useCreateFund();

  // React Hook Form with Zod validation
  const form = useForm<CreateFundFormData>({
    schema: createFundSchema,
    defaultValues: {
      name: '',
      entity_id: 0,
      company_id: companyId,
      tracking_type: FundTrackingType.NAV_BASED,
      tax_jurisdiction: Country.AU,
      currency: Currency.AUD,
      fund_investment_type: undefined,
      description: undefined,
      expected_irr: undefined,
      expected_duration_months: undefined,
      commitment_amount: undefined,
    },
    onSubmit: async (data) => {
      // Transform form data to API request format
      const requestData = transformCreateFundForm({
        ...data,
        company_id: companyId, // Ensure company_id is set
      });
      
      await createFund(requestData);
    },
  });

  // Handle success flow when fund is created
  useEffect(() => {
    if (createdFund) {
      onFundCreated();
      onClose();
      form.reset();
      setSelectedTemplate(null);
      setShowTemplateSelection(true);
    }
  }, [createdFund, onFundCreated, onClose, form]);

  // Reset form when modal opens
  useEffect(() => {
    if (open) {
      form.reset({
        name: '',
        entity_id: 0,
        company_id: companyId,
        tracking_type: FundTrackingType.NAV_BASED,
        tax_jurisdiction: Country.AU,
        currency: Currency.AUD,
        fund_investment_type: undefined,
        description: undefined,
        expected_irr: undefined,
        expected_duration_months: undefined,
        commitment_amount: undefined,
      });
      setSelectedTemplate(null);
      setShowTemplateSelection(true);
    }
  }, [open, companyId, form]);

  // Apply template to form data
  const applyTemplate = (template: FundTemplate) => {
    const trackingType = template.tracking_type === 'nav_based' 
      ? FundTrackingType.NAV_BASED 
      : FundTrackingType.COST_BASED;
    
    const currencyEnum = template.currency as Currency;
    
    form.reset({
      name: '',
      entity_id: 0,
      company_id: companyId,
      tracking_type: trackingType,
      tax_jurisdiction: Country.AU, // Default, user can change
      currency: currencyEnum,
      fund_investment_type: undefined,
      description: template.description_template || undefined,
      expected_irr: template.expected_irr,
      expected_duration_months: template.expected_duration_months,
      commitment_amount: template.commitment_amount,
    });

    setSelectedTemplate(template);
    setShowTemplateSelection(false);
  };

  // Handle form submission
  const handleFormSubmit = () => {
    if (showTemplateSelection) return;
    form.handleSubmit();
  };

  // Handle modal close
  const handleClose = () => {
    if (!isSubmitting && !form.formState.isSubmitting) {
      onClose();
      form.reset();
      setSelectedTemplate(null);
      setShowTemplateSelection(true);
    }
  };

  // Handle entity creation
  const handleEntityCreated = (entity: { id: number; name: string }) => {
    form.setValue('entity_id', entity.id);
    form.clearErrors('entity_id');
  };

  // Form validation status - check required fields
  const isFormValid = () => {
    if (showTemplateSelection) return true;
    
    const values = form.getValues();
    const requiredFields = ['entity_id', 'name', 'tracking_type', 'tax_jurisdiction', 'currency'];
    
    const requiredFieldsValid = requiredFields.every(field => {
      const value = values[field as keyof CreateFundFormData];
      if (field === 'entity_id') {
        return typeof value === 'number' && value > 0;
      }
      return value !== undefined && value !== null && value !== '';
    });
    
    return requiredFieldsValid && form.formState.isValid;
  };

  // Form progress calculation
  const getFormProgress = () => {
    const values = form.getValues();
    const requiredFields = ['entity_id', 'name', 'tracking_type', 'tax_jurisdiction', 'currency'];
    const completedFields = requiredFields.filter(field => {
      const value = values[field as keyof CreateFundFormData];
      if (field === 'entity_id') {
        return typeof value === 'number' && value > 0;
      }
      return value !== undefined && value !== null && value !== '';
    });
    return (completedFields.length / requiredFields.length) * 100;
  };

  // Validation status
  const getValidationStatus = () => {
    const values = form.getValues();
    const requiredFields = ['entity_id', 'name', 'tracking_type', 'tax_jurisdiction', 'currency'];
    const missingFields = requiredFields.filter(field => {
      const value = values[field as keyof CreateFundFormData];
      if (field === 'entity_id') {
        return !(typeof value === 'number' && value > 0);
      }
      return value === undefined || value === null || value === '';
    });
    
    const errorFields = Object.keys(form.formState.errors).filter(
      key => form.formState.errors[key as keyof CreateFundFormData]
    );
    
    return {
      missingFields,
      errorFields,
      hasErrors: errorFields.length > 0,
      isComplete: missingFields.length === 0 && errorFields.length === 0
    };
  };

  return (
    <FormProvider {...form}>
      <FormModal
        open={open}
        title="Create New Fund"
        subtitle={`Adding fund to ${companyName}`}
        onClose={handleClose}
        onSubmit={handleFormSubmit}
        isSubmitting={isSubmitting || form.formState.isSubmitting}
        isValid={!showTemplateSelection ? isFormValid() : true}
        isDirty={form.formState.isDirty}
        showCloseConfirmation={true}
        maxWidth="md"
        fullWidth={true}
        actions={
        <>
          {!showTemplateSelection && selectedTemplate && (
            <Button 
              onClick={() => setShowTemplateSelection(true)} 
              variant="outlined" 
              disabled={isSubmitting || form.formState.isSubmitting} 
              startIcon={<AddIcon />}
            >
              Back to Templates
            </Button>
          )}
          <Button 
            onClick={handleFormSubmit} 
            variant="contained" 
            disabled={isSubmitting || form.formState.isSubmitting || !isFormValid()}
            startIcon={isSubmitting || form.formState.isSubmitting ? <CircularProgress size={20} /> : null}
          >
            {isSubmitting || form.formState.isSubmitting ? 'Creating Fund...' : 'Create Fund'}
          </Button>
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
                control={form.control}
                entities={entities || []}
                onCreateEntity={() => setShowEntityModal(true)}
                trackingTypeLocked={!!selectedTemplate}
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
      </FormModal>
    </FormProvider>
  );
};

export default CreateFundModal;
