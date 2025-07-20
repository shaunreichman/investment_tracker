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
  Typography
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

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
  };

  const handleSubmit = async () => {
    // Validation
    if (!formData.entity_id || !formData.name || !formData.fund_type || !formData.tracking_type) {
      setError('Please fill in all required fields');
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
          name: formData.name,
          fund_type: formData.fund_type,
          tracking_type: formData.tracking_type,
          currency: formData.currency,
          commitment_amount: formData.commitment_amount ? parseFloat(formData.commitment_amount) : null,
          expected_irr: formData.expected_irr ? parseFloat(formData.expected_irr) : null,
          expected_duration_months: formData.expected_duration_months ? parseInt(formData.expected_duration_months) : null,
          description: formData.description || null
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
      }, 1500);

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
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center">
          <AddIcon sx={{ mr: 1 }} />
          Create New Fund
        </Box>
        <Typography variant="body2" color="textSecondary">
          Adding fund to {companyName}
        </Typography>
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Fund created successfully!
          </Alert>
        )}

        {loading ? (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        ) : (
          <Box display="grid" gap={3} sx={{ gridTemplateColumns: '1fr 1fr' }}>
            {/* Entity Selection */}
            <FormControl fullWidth>
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
            </FormControl>

            {/* Fund Name */}
            <TextField
              fullWidth
              label="Fund Name *"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
            />

            {/* Fund Type */}
            <FormControl fullWidth>
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
            </FormControl>

            {/* Tracking Type */}
            <FormControl fullWidth>
              <InputLabel>Tracking Type *</InputLabel>
              <Select
                value={formData.tracking_type}
                onChange={(e) => handleInputChange('tracking_type', e.target.value)}
                label="Tracking Type *"
              >
                <MenuItem value="nav_based">NAV-Based (Units & NAV)</MenuItem>
                <MenuItem value="cost_based">Cost-Based (Capital Calls)</MenuItem>
              </Select>
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
              helperText="Total commitment amount (optional)"
            />

            {/* Expected IRR */}
            <TextField
              fullWidth
              label="Expected IRR (%)"
              type="number"
              value={formData.expected_irr}
              onChange={(e) => handleInputChange('expected_irr', e.target.value)}
              helperText="Expected annual return (optional)"
            />

            {/* Expected Duration */}
            <TextField
              fullWidth
              label="Expected Duration (months)"
              type="number"
              value={formData.expected_duration_months}
              onChange={(e) => handleInputChange('expected_duration_months', e.target.value)}
              helperText="Expected fund duration in months (optional)"
            />

            {/* Description */}
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              sx={{ gridColumn: '1 / -1' }}
            />
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={submitting}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={submitting || !formData.entity_id || !formData.name || !formData.fund_type || !formData.tracking_type}
          startIcon={submitting ? <CircularProgress size={20} /> : <AddIcon />}
        >
          {submitting ? 'Creating...' : 'Create Fund'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateFundModal; 