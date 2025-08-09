import React, { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, CircularProgress, Typography, Paper } from '@mui/material';
import { ErrorDisplay } from '../../ErrorDisplay';
import { Add as AddIcon, CheckCircle as CheckCircleIcon, AccountBalance as AccountBalanceIcon, TrendingUp as TrendingUpIcon } from '@mui/icons-material';
import CreateEntityModal from '../../CreateEntityModal';
import { useEntities } from '../../../hooks/useEntities';
import { useCreateFund } from '../../../hooks/useFunds';
import { FundType } from '../../../types/api';
import { validateField } from '../../../utils/validators';
import TemplateSelectionSection from './TemplateSelectionSection';
import FundFormSection from './FundFormSection';

interface CreateFundModalProps {
  open: boolean;
  onClose: () => void;
  onFundCreated: () => void;
  companyId: number;
  companyName: string;
}

interface ValidationErrors {
  entity_id?: string;
  name?: string;
  fund_type?: string;
  tracking_type?: string;
  commitment_amount?: string;
  expected_irr?: string;
  expected_duration_months?: string;
  description?: string;
}

// Fund type templates with predefined values
interface FundTemplate {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  fund_type: string;
  tracking_type: 'nav_based' | 'cost_based';
  currency: string;
  commitment_amount?: number;
  expected_irr?: number;
  expected_duration_months?: number;
  description_template: string;
}

const FUND_TEMPLATES: FundTemplate[] = [
  {
    id: 'cost-based',
    name: 'Cost-Based Fund',
    description: 'Track investments using capital calls and returns',
    icon: <AccountBalanceIcon />,
    fund_type: '',
    tracking_type: 'cost_based',
    currency: 'AUD',
    description_template: ''
  },
  {
    id: 'nav-based',
    name: 'NAV-Based Fund',
    description: 'Track investments using units and NAV per share',
    icon: <TrendingUpIcon />,
    fund_type: '',
    tracking_type: 'nav_based',
    currency: 'AUD',
    description_template: ''
  }
];

const CreateFundModal: React.FC<CreateFundModalProps> = ({
  open,
  onClose,
  onFundCreated,
  companyId,
  companyName
}) => {
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [showEntityModal, setShowEntityModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<FundTemplate | null>(null);
  const [showTemplateSelection, setShowTemplateSelection] = useState(true);

  // Form fields
  const [formData, setFormData] = useState({
    entity_id: '',
    name: '',
    fund_type: '',
    tracking_type: '',
    currency: 'AUD',
    commitment_amount: '',
    expected_irr: '',
    expected_duration_months: '',
    description: ''
  });

  // Centralized API hooks
  const { data: entities, loading, error } = useEntities({ refetchOnWindowFocus: true });
  const { mutate: createFund } = useCreateFund();

  // Reset form when modal opens
  useEffect(() => {
    if (open) {
      setFormData({
        entity_id: '',
        name: '',
        fund_type: '',
        tracking_type: '',
        currency: 'AUD',
        commitment_amount: '',
        expected_irr: '',
        expected_duration_months: '',
        description: ''
      });
      setSelectedTemplate(null);
      setShowTemplateSelection(true);
      setValidationErrors({});
      setSuccess(false);
      setSubmitting(false);
    }
  }, [open]);

  // Apply template to form data
  const applyTemplate = (template: FundTemplate) => {
    setFormData({
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
    setValidationErrors(prev => ({
      ...prev,
      tracking_type: undefined,
      currency: undefined,
      fund_type: template.fund_type ? undefined : prev.fund_type,
      commitment_amount: template.commitment_amount ? undefined : prev.commitment_amount,
      expected_irr: template.expected_irr ? undefined : prev.expected_irr,
      expected_duration_months: template.expected_duration_months ? undefined : prev.expected_duration_months,
      description: template.description_template ? undefined : prev.description
    }));
  };

  const resetToTemplateSelection = () => {
    setSelectedTemplate(null);
    setShowTemplateSelection(true);
    setFormData({
      entity_id: '',
      name: '',
      fund_type: '',
      tracking_type: '',
      currency: 'AUD',
      commitment_amount: '',
      expected_irr: '',
      expected_duration_months: '',
      description: ''
    });
    setValidationErrors({});
  };

  const validateForm = (): boolean => {
    const errors: ValidationErrors = {};
    if (!formData.entity_id) errors.entity_id = 'Entity is required';
    if (!formData.name.trim()) errors.name = 'Fund name is required';
    if (!formData.fund_type) errors.fund_type = 'Fund type is required';
    if (!formData.tracking_type) errors.tracking_type = 'Tracking type is required';

    const nameError = validateField('name', formData.name);
    if (nameError) errors.name = nameError;
    const fundTypeError = validateField('fund_type', formData.fund_type);
    if (fundTypeError) errors.fund_type = fundTypeError;
    const commitmentError = validateField('commitment_amount', formData.commitment_amount);
    if (commitmentError) errors.commitment_amount = commitmentError;
    const irrError = validateField('expected_irr', formData.expected_irr);
    if (irrError) errors.expected_irr = irrError;
    const durationError = validateField('expected_duration_months', formData.expected_duration_months);
    if (durationError) errors.expected_duration_months = durationError;
    const descriptionError = validateField('description', formData.description);
    if (descriptionError) errors.description = descriptionError;

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  useEffect(() => {
    if (open) {
      validateForm();
    }
  }, [open]);

  useEffect(() => {
    if (open && !showTemplateSelection) {
      validateForm();
    }
  }, [formData, open, showTemplateSelection]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    const error = validateField(field, value);
    setValidationErrors(prev => ({
      ...prev,
      [field]: error || undefined
    }));
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;
    try {
      setSubmitting(true);
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
      setSuccess(true);
      setTimeout(() => {
        onFundCreated();
        onClose();
        setSuccess(false);
        setFormData({
          entity_id: '',
          name: '',
          fund_type: '',
          tracking_type: '',
          currency: 'AUD',
          commitment_amount: '',
          expected_irr: '',
          expected_duration_months: '',
          description: ''
        });
        setValidationErrors({});
      }, 2000);
    } catch (err) {
      // handled by hook
      console.error('Failed to create fund:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!submitting) {
      onClose();
      setSuccess(false);
      setValidationErrors({});
      setFormData({
        entity_id: '',
        name: '',
        fund_type: '',
        tracking_type: '',
        currency: 'AUD',
        commitment_amount: '',
        expected_irr: '',
        expected_duration_months: '',
        description: ''
      });
      setSelectedTemplate(null);
      setShowTemplateSelection(true);
    }
  };

  const handleEntityCreated = (entity: { id: number; name: string }) => {
    setFormData(prev => ({
      ...prev,
      entity_id: entity.id.toString()
    }));
    setValidationErrors(prev => ({
      ...prev,
      entity_id: undefined
    }));
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
          {submitting && (
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
          <Box sx={{ mb: 2, p: 2, bgcolor: 'success.light', borderRadius: 1, display: 'flex', alignItems: 'center' }}>
            <CheckCircleIcon color="success" sx={{ mr: 1 }} />
            <Box>
              <Typography variant="body1" fontWeight="medium" color="success.main">
                Fund created successfully!
              </Typography>
              <Typography variant="body2" color="success.main">
                Redirecting to fund details...
              </Typography>
            </Box>
          </Box>
        )}

        {/* Error State */}
        {error && (
          <ErrorDisplay
            error={error}
            canRetry={error.retryable}
            onRetry={() => handleSubmit()}
            onDismiss={() => {}}
            variant="inline"
          />
        )}

        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" p={4}>
            <Box textAlign="center">
              <CircularProgress size={40} sx={{ mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                Loading entities...
              </Typography>
            </Box>
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
          <Button onClick={() => setShowTemplateSelection(true)} variant="outlined" disabled={submitting} startIcon={<AddIcon />}>
            Back to Templates
          </Button>
        )}
        <Button onClick={handleClose} disabled={submitting} variant="outlined">
          Cancel
        </Button>
        {!showTemplateSelection && (
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={submitting || !isFormValid()}
            startIcon={submitting ? <CircularProgress size={20} /> : <AddIcon />}
            sx={{ minWidth: 120 }}
            title={!isFormValid() ? 'Please fill in all required fields and fix any validation errors' : ''}
          >
            {submitting ? 'Creating...' : 'Create Fund'}
          </Button>
        )}
      </DialogActions>

      {/* Entity Creation Modal */}
      <CreateEntityModal open={showEntityModal} onClose={() => setShowEntityModal(false)} onEntityCreated={handleEntityCreated} />
    </Dialog>
  );
};

export default CreateFundModal;


