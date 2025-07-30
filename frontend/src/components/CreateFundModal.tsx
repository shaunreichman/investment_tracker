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
  Alert,
  Typography,
  FormHelperText,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Divider,
  InputAdornment
} from '@mui/material';
import { Add as AddIcon, CheckCircle as CheckCircleIcon, Error as ErrorIcon, AccountBalance as AccountBalanceIcon, TrendingUp as TrendingUpIcon } from '@mui/icons-material';
import CreateEntityModal from './CreateEntityModal';
import { useEntities } from '../hooks/useEntities';
import { useCreateFund } from '../hooks/useFunds';
import { Entity, FundType } from '../types/api';



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

  // Use our centralized API hooks
  const { data: entities, loading, error } = useEntities({ refetchOnWindowFocus: true });
  const { mutate: createFund, loading: isCreating, error: createError } = useCreateFund();

  // Number formatting helpers
  const formatNumber = (value: string): string => {
    if (!value) return '';
    const num = parseFloat(value.replace(/,/g, ''));
    if (isNaN(num)) return value;
    return num.toLocaleString('en-US');
  };

  const parseNumber = (value: string): string => {
    if (!value) return '';
    return value.replace(/,/g, '');
  };

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

  // Reset to template selection
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

  // Validation rules
  const validateField = (field: string, value: string): string | undefined => {
    switch (field) {
      case 'name':
        if (!value.trim()) return 'Fund name is required';
        if (value.trim().length < 2) return 'Fund name must be at least 2 characters';
        if (value.trim().length > 255) return 'Fund name must be less than 255 characters';
        if (!/^[a-zA-Z0-9\s\-_()]+$/.test(value.trim())) {
          return 'Fund name can only contain letters, numbers, spaces, hyphens, underscores, and parentheses';
        }
        break;
      
      case 'fund_type':
        if (!value.trim()) return 'Fund type is required';
        if (value.trim().length < 2) return 'Fund type must be at least 2 characters';
        if (value.trim().length > 100) return 'Fund type must be less than 100 characters';
        break;
      
      case 'commitment_amount':
        if (value && value.trim() !== '') {
          const num = parseFloat(value);
          if (isNaN(num)) return 'Commitment amount must be a valid number';
          if (num <= 0) return 'Commitment amount must be positive';
          if (num > 999999999) return 'Commitment amount must be less than 1 billion';
        }
        break;
      
      case 'expected_irr':
        if (value && value.trim() !== '') {
          const num = parseFloat(value);
          if (isNaN(num)) return 'Expected IRR must be a valid number';
          if (num < 0 || num > 100) return 'Expected IRR must be between 0 and 100';
        }
        break;
      
      case 'expected_duration_months':
        if (value && value.trim() !== '') {
          const num = parseInt(value);
          if (isNaN(num)) return 'Expected duration must be a valid number';
          if (num < 1 || num > 1200) return 'Expected duration must be between 1 and 1200 months';
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

  const validateForm = (): boolean => {
    const errors: ValidationErrors = {};
    
    // Required fields
    if (!formData.entity_id) {
      errors.entity_id = 'Entity is required';
    }
    if (!formData.name.trim()) {
      errors.name = 'Fund name is required';
    }
    if (!formData.fund_type) {
      errors.fund_type = 'Fund type is required';
    }
    if (!formData.tracking_type) {
      errors.tracking_type = 'Tracking type is required';
    }
    
    // Field-specific validation
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
      validateForm(); // Trigger validation when modal opens
    }
  }, [open]);

  // Trigger validation when form data changes
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
    
    // Real-time validation
    const error = validateField(field, value);
    setValidationErrors(prev => ({
      ...prev,
      [field]: error || undefined // Ensure undefined instead of empty string
    }));
  };

  const handleSubmit = async () => {
    // Validate form
    if (!validateForm()) {
      return;
    }

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
      // Error handling is managed by the hook
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
      // Clear form data when closing
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
      // Reset template selection state
      setSelectedTemplate(null);
      setShowTemplateSelection(true);
    }
  };

  const handleEntityCreated = (entity: { id: number; name: string }) => {
    // Select the new entity (the hook will automatically refetch entities)
    setFormData(prev => ({
      ...prev,
      entity_id: entity.id.toString()
    }));
    // Clear entity validation error
    setValidationErrors(prev => ({
      ...prev,
      entity_id: undefined
    }));
  };

  const isFormValid = () => {
    // Check required fields are filled
    const requiredFieldsValid = formData.entity_id && 
                               formData.name.trim() && 
                               formData.fund_type && 
                               formData.tracking_type;
    
    // Check there are no validation errors (only count actual error messages)
    const noValidationErrors = Object.values(validationErrors).every(error => !error);
    
    return requiredFieldsValid && noValidationErrors;
  };

  const getFormProgress = () => {
    const requiredFields = ['entity_id', 'name', 'fund_type', 'tracking_type'];
    const completedFields = requiredFields.filter(field => {
      const value = formData[field as keyof typeof formData];
      return value && value.toString().trim() !== '';
    });
    return (completedFields.length / requiredFields.length) * 100;
  };

  const getValidationStatus = () => {
    const requiredFields = ['entity_id', 'name', 'fund_type', 'tracking_type'];
    const missingFields = requiredFields.filter(field => {
      const value = formData[field as keyof typeof formData];
      return !value || value.toString().trim() === '';
    });
    
    const errorFields = Object.keys(validationErrors).filter(key => validationErrors[key as keyof ValidationErrors]);
    
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
          <Alert 
            severity="success" 
            sx={{ mb: 2 }}
            icon={<CheckCircleIcon />}
          >
            <Typography variant="body1" fontWeight="medium">
              Fund created successfully!
            </Typography>
            <Typography variant="body2">
              Redirecting to fund details...
            </Typography>
          </Alert>
        )}

        {/* Error State */}
        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 2 }}
            icon={<ErrorIcon />}
          >
            <Typography variant="body1" fontWeight="medium">
              Error creating fund
            </Typography>
            <Typography variant="body2">
              {error}
            </Typography>
          </Alert>
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
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
                  Select a Tracking Type Template
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Choose how you want to track your fund investments.
                </Typography>
                <Box display="grid" gap={2} sx={{ gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
                  {FUND_TEMPLATES.map((template) => (
                    <Paper key={template.id} sx={{ cursor: 'pointer', p: 2, '&:hover': { bgcolor: 'primary.light' } }}>
                      <Box onClick={() => applyTemplate(template)}>
                        <Box display="flex" alignItems="center" gap={2} sx={{ mb: 1 }}>
                          {template.icon}
                          <Typography variant="h6">{template.name}</Typography>
                        </Box>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {template.description}
                        </Typography>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          <Typography variant="caption" sx={{ 
                            bgcolor: 'primary.main', 
                            color: 'white', 
                            px: 1, 
                            py: 0.5, 
                            borderRadius: 1,
                            fontSize: '0.75rem'
                          }}>
                            {template.tracking_type}
                          </Typography>
                          <Typography variant="caption" sx={{ 
                            bgcolor: 'grey.300', 
                            px: 1, 
                            py: 0.5, 
                            borderRadius: 1,
                            fontSize: '0.75rem'
                          }}>
                            {template.currency}
                          </Typography>
                        </Box>
                      </Box>
                    </Paper>
                  ))}
                </Box>
              </Box>
            ) : (
              <Box>
                {selectedTemplate && (
                  <Box sx={{ mb: 3, p: 2, bgcolor: 'primary.light', borderRadius: 1 }}>
                    <Box display="flex" alignItems="center" gap={2}>
                      {selectedTemplate.icon}
                      <Typography variant="h6">
                        Using Template: {selectedTemplate.name}
                      </Typography>
                      <Typography variant="caption" sx={{ 
                        bgcolor: 'primary.main', 
                        color: 'white', 
                        px: 1, 
                        py: 0.5, 
                        borderRadius: 1,
                        fontSize: '0.75rem'
                      }}>
                        {selectedTemplate.tracking_type}
                      </Typography>
                      <Typography variant="caption" sx={{ 
                        bgcolor: 'grey.300', 
                        px: 1, 
                        py: 0.5, 
                        borderRadius: 1,
                        fontSize: '0.75rem'
                      }}>
                        {selectedTemplate.currency}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {selectedTemplate.description}
                    </Typography>
                  </Box>
                )}
              
              <Box display="grid" gap={3} sx={{ gridTemplateColumns: '1fr 1fr' }}>
              {/* Entity Selection */}
              <FormControl fullWidth error={!!validationErrors.entity_id} required>
                <InputLabel>Entity *</InputLabel>
                <Select
                  value={formData.entity_id}
                  onChange={(e) => handleInputChange('entity_id', e.target.value)}
                  label="Entity *"
                >
                  {entities?.map((entity) => (
                    <MenuItem key={entity.id} value={entity.id}>
                      {entity.name}
                    </MenuItem>
                  ))}
                  <Divider />
                  <MenuItem 
                    value="create_new" 
                    onClick={() => setShowEntityModal(true)}
                    sx={{ 
                      color: 'primary.main',
                      fontStyle: 'italic'
                    }}
                  >
                    <AddIcon sx={{ mr: 1, fontSize: 16 }} />
                    Create New Entity...
                  </MenuItem>
                </Select>
                {validationErrors.entity_id && (
                  <FormHelperText error>{validationErrors.entity_id}</FormHelperText>
                )}
              </FormControl>

              {/* Fund Name */}
              <TextField
                fullWidth
                label="Fund Name *"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                error={!!validationErrors.name}
                helperText={validationErrors.name || "Enter a unique fund name (2-255 characters)"}
                required
              />

              {/* Fund Type */}
              <FormControl fullWidth error={!!validationErrors.fund_type} required>
                <InputLabel>Fund Type *</InputLabel>
                <Select
                  value={formData.fund_type}
                  onChange={(e) => handleInputChange('fund_type', e.target.value)}
                  label="Fund Type *"
                >
                  <MenuItem value="Private Equity">Private Equity</MenuItem>
                  <MenuItem value="Private Debt">Private Debt</MenuItem>
                  <MenuItem value="Venture Capital">Venture Capital</MenuItem>
                  <MenuItem value="Real Estate">Real Estate</MenuItem>
                  <MenuItem value="Infrastructure">Infrastructure</MenuItem>
                  <MenuItem value="Hedge Fund">Hedge Fund</MenuItem>
                  <MenuItem value="Equity - Consumer Discretionary">Equity - Consumer Discretionary</MenuItem>
                  <MenuItem value="Equity - Technology">Equity - Technology</MenuItem>
                  <MenuItem value="Equity - Financial">Equity - Financial</MenuItem>
                  <MenuItem value="Other">Other</MenuItem>
                </Select>
                {validationErrors.fund_type && (
                  <FormHelperText error>{validationErrors.fund_type}</FormHelperText>
                )}
              </FormControl>

              {/* Tracking Type */}
              <FormControl fullWidth error={!!validationErrors.tracking_type} required>
                <InputLabel>Tracking Type *</InputLabel>
                <Select
                  value={formData.tracking_type}
                  onChange={(e) => handleInputChange('tracking_type', e.target.value)}
                  label="Tracking Type *"
                >
                  <MenuItem value="nav_based">NAV-Based (Units & NAV)</MenuItem>
                  <MenuItem value="cost_based">Cost-Based (Capital Calls)</MenuItem>
                </Select>
                {validationErrors.tracking_type && (
                  <FormHelperText error>{validationErrors.tracking_type}</FormHelperText>
                )}
              </FormControl>

              {/* Currency */}
              <FormControl fullWidth>
                <InputLabel>Currency</InputLabel>
                <Select
                  value={formData.currency}
                  onChange={(e) => handleInputChange('currency', e.target.value)}
                  label="Currency"
                >
                  <MenuItem value="AUD">AUD</MenuItem>
                  <MenuItem value="USD">USD</MenuItem>
                  <MenuItem value="EUR">EUR</MenuItem>
                  <MenuItem value="GBP">GBP</MenuItem>
                </Select>
              </FormControl>

              {/* Commitment Amount */}
              <TextField
                fullWidth
                label="Commitment Amount"
                value={formatNumber(formData.commitment_amount)}
                onChange={(e) => handleInputChange('commitment_amount', parseNumber(e.target.value))}
                error={!!validationErrors.commitment_amount}
                helperText={validationErrors.commitment_amount || "Total commitment amount (optional)"}
                inputProps={{
                  style: { textAlign: 'left' }
                }}
              />

              {/* Expected IRR */}
              <TextField
                fullWidth
                label="Expected IRR (%)"
                type="number"
                value={formData.expected_irr}
                onChange={(e) => handleInputChange('expected_irr', e.target.value)}
                error={!!validationErrors.expected_irr}
                helperText={validationErrors.expected_irr || "Expected annual return 0-100% (optional)"}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <Typography variant="body2" color="text.secondary">
                        %
                      </Typography>
                    </InputAdornment>
                  ),
                }}
              />

              {/* Expected Duration */}
              <TextField
                fullWidth
                label="Expected Duration (months)"
                type="number"
                value={formData.expected_duration_months}
                onChange={(e) => handleInputChange('expected_duration_months', e.target.value)}
                error={!!validationErrors.expected_duration_months}
                helperText={validationErrors.expected_duration_months || "Expected fund duration 1-1200 months (optional)"}
              />

              {/* Description */}
              <TextField
                fullWidth
                label="Description"
                multiline
                minRows={3}
                maxRows={6}
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                error={!!validationErrors.description}
                helperText={validationErrors.description || "Optional fund description (max 1000 characters)"}
                sx={{ gridColumn: '1 / -1' }}
                variant="outlined"
              />
            </Box>
              </Box>
            )}
          </Paper>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        {!showTemplateSelection && selectedTemplate && (
          <Button 
            onClick={() => setShowTemplateSelection(true)}
            variant="outlined"
            disabled={submitting}
            startIcon={<AddIcon />}
          >
            Back to Templates
          </Button>
        )}
        <Button 
          onClick={handleClose} 
          disabled={submitting}
          variant="outlined"
        >
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
      <CreateEntityModal
        open={showEntityModal}
        onClose={() => setShowEntityModal(false)}
        onEntityCreated={handleEntityCreated}
      />
    </Dialog>
  );
};

export default CreateFundModal; 