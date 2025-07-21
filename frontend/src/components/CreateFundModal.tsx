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
  Divider
} from '@mui/material';
import { Add as AddIcon, CheckCircle as CheckCircleIcon, Error as ErrorIcon } from '@mui/icons-material';

interface Entity {
  id: number;
  name: string;
}

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

const CreateFundModal: React.FC<CreateFundModalProps> = ({
  open,
  onClose,
  onFundCreated,
  companyId,
  companyName
}) => {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});

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

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

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
    if (!formData.entity_id) errors.entity_id = 'Entity is required';
    if (!formData.name.trim()) errors.name = 'Fund name is required';
    if (!formData.fund_type) errors.fund_type = 'Fund type is required';
    if (!formData.tracking_type) errors.tracking_type = 'Tracking type is required';
    
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

  const fetchEntities = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/entities`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch entities');
      }

      const data = await response.json();
      setEntities(data.entities);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [API_BASE_URL]);

  useEffect(() => {
    if (open) {
      fetchEntities();
    }
  }, [open, fetchEntities]);

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
    setError(null);
    
    // Validate form
    if (!validateForm()) {
      setError('Please fix the validation errors before submitting');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/funds`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          investment_company_id: companyId,
          entity_id: parseInt(formData.entity_id),
          name: formData.name.trim(),
          fund_type: formData.fund_type,
          tracking_type: formData.tracking_type,
          currency: formData.currency,
          commitment_amount: formData.commitment_amount ? parseFloat(formData.commitment_amount) : null,
          expected_irr: formData.expected_irr ? parseFloat(formData.expected_irr) : null,
          expected_duration_months: formData.expected_duration_months ? parseInt(formData.expected_duration_months) : null,
          description: formData.description.trim() || null
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create fund');
      }

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
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!submitting) {
      onClose();
      setError(null);
      setSuccess(false);
      setValidationErrors({});
    }
  };

  const isFormValid = () => {
    return formData.entity_id && 
           formData.name.trim() && 
           formData.fund_type && 
           formData.tracking_type &&
           Object.keys(validationErrors).length === 0;
  };

  const getFormProgress = () => {
    const requiredFields = ['entity_id', 'name', 'fund_type', 'tracking_type'];
    const completedFields = requiredFields.filter(field => {
      const value = formData[field as keyof typeof formData];
      return value && value.toString().trim() !== '';
    });
    return (completedFields.length / requiredFields.length) * 100;
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
            
            <Box display="grid" gap={3} sx={{ gridTemplateColumns: '1fr 1fr' }}>
              {/* Entity Selection */}
              <FormControl fullWidth error={!!validationErrors.entity_id}>
                <InputLabel>Entity *</InputLabel>
                <Select
                  value={formData.entity_id}
                  onChange={(e) => handleInputChange('entity_id', e.target.value)}
                  label="Entity *"
                >
                  {entities.map((entity) => (
                    <MenuItem key={entity.id} value={entity.id}>
                      {entity.name}
                    </MenuItem>
                  ))}
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
              />

              {/* Fund Type */}
              <FormControl fullWidth error={!!validationErrors.fund_type}>
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
              <FormControl fullWidth error={!!validationErrors.tracking_type}>
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
                type="number"
                value={formData.commitment_amount}
                onChange={(e) => handleInputChange('commitment_amount', e.target.value)}
                error={!!validationErrors.commitment_amount}
                helperText={validationErrors.commitment_amount || "Total commitment amount in AUD (optional)"}
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
                rows={3}
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                error={!!validationErrors.description}
                helperText={validationErrors.description || "Optional fund description (max 1000 characters)"}
                sx={{ gridColumn: '1 / -1' }}
              />
            </Box>
          </Paper>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button 
          onClick={handleClose} 
          disabled={submitting}
          variant="outlined"
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={submitting || !isFormValid()}
          startIcon={submitting ? <CircularProgress size={20} /> : <AddIcon />}
          sx={{ minWidth: 120 }}
        >
          {submitting ? 'Creating...' : 'Create Fund'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateFundModal; 