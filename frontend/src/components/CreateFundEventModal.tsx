import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Box,
  Alert,
  CircularProgress,
  Typography
} from '@mui/material';

interface CreateFundEventModalProps {
  open: boolean;
  onClose: () => void;
  onEventCreated: () => void;
  fundId: number;
  fundTrackingType: 'nav_based' | 'cost_based';
}

type EventType = 'CAPITAL_CALL' | 'DISTRIBUTION' | 'UNIT_PURCHASE' | 'UNIT_SALE';

const EVENT_TEMPLATES: { label: string; value: EventType; description: string; trackingType: 'nav_based' | 'cost_based' | 'both' }[] = [
  { label: 'Capital Call', value: 'CAPITAL_CALL', description: 'Add a capital call (cost-based funds)', trackingType: 'cost_based' },
  { label: 'Distribution', value: 'DISTRIBUTION', description: 'Add a distribution (all funds)', trackingType: 'both' },
  { label: 'Unit Purchase', value: 'UNIT_PURCHASE', description: 'Buy units (NAV-based funds)', trackingType: 'nav_based' },
  { label: 'Unit Sale', value: 'UNIT_SALE', description: 'Sell units (NAV-based funds)', trackingType: 'nav_based' },
];

const CreateFundEventModal: React.FC<CreateFundEventModalProps> = ({ open, onClose, onEventCreated, fundId, fundTrackingType }) => {
  const [eventType, setEventType] = useState<EventType | ''>('');
  const [formData, setFormData] = useState<any>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

  const resetForm = () => {
    setEventType('');
    setFormData({});
    setError(null);
    setSuccess(false);
  };

  const handleClose = () => {
    if (!submitting) {
      resetForm();
      onClose();
    }
  };

  const handleEventTypeChange = (value: EventType) => {
    setEventType(value);
    setFormData({});
    setError(null);
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }));
  };

  const validate = () => {
    if (!eventType) return false;
    if (!formData.event_date) return false;
    if (eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION') {
      if (!formData.amount) return false;
    }
    if (eventType === 'UNIT_PURCHASE') {
      if (!formData.units_purchased || !formData.unit_price) return false;
    }
    if (eventType === 'UNIT_SALE') {
      if (!formData.units_sold || !formData.unit_price) return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    setError(null);
    if (!validate()) {
      setError('Please fill in all required fields.');
      return;
    }
    setSubmitting(true);
    try {
      const payload: any = {
        event_type: eventType,
        event_date: formData.event_date,
        description: formData.description,
        reference_number: formData.reference_number,
      };
      if (eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION') {
        payload.amount = parseFloat(formData.amount);
        if (eventType === 'DISTRIBUTION' && formData.distribution_type) {
          payload.distribution_type = formData.distribution_type;
        }
      }
      if (eventType === 'UNIT_PURCHASE') {
        payload.units_purchased = parseFloat(formData.units_purchased);
        payload.unit_price = parseFloat(formData.unit_price);
        payload.brokerage_fee = formData.brokerage_fee ? parseFloat(formData.brokerage_fee) : 0.0;
      }
      if (eventType === 'UNIT_SALE') {
        payload.units_sold = parseFloat(formData.units_sold);
        payload.unit_price = parseFloat(formData.unit_price);
        payload.brokerage_fee = formData.brokerage_fee ? parseFloat(formData.brokerage_fee) : 0.0;
      }
      const response = await fetch(`${API_BASE_URL}/api/funds/${fundId}/events`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Failed to create event');
      }
      setSuccess(true);
      setTimeout(() => {
        resetForm();
        onEventCreated();
        onClose();
      }, 1000);
    } catch (err: any) {
      setError(err.message || 'Failed to create event');
    } finally {
      setSubmitting(false);
    }
  };

  // Filter templates by fund type
  const availableTemplates = EVENT_TEMPLATES.filter(t => t.trackingType === fundTrackingType || t.trackingType === 'both');

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Add Cash Flow Event</DialogTitle>
      <DialogContent>
        {success && <Alert severity="success">Event created successfully!</Alert>}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <Box sx={{ mb: 2 }}>
          <TextField
            select
            label="Event Type"
            value={eventType}
            onChange={e => handleEventTypeChange(e.target.value as EventType)}
            fullWidth
            required
            sx={{ mb: 2 }}
          >
            {availableTemplates.map(t => (
              <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>
            ))}
          </TextField>
        </Box>
        {eventType && (
          <Box display="flex" flexDirection="column" gap={2}>
            <TextField
              label="Event Date"
              type="date"
              value={formData.event_date || ''}
              onChange={e => handleInputChange('event_date', e.target.value)}
              InputLabelProps={{ shrink: true }}
              required
            />
            {(eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION') && (
              <TextField
                label="Amount"
                type="number"
                value={formData.amount || ''}
                onChange={e => handleInputChange('amount', e.target.value)}
                required
              />
            )}
            {eventType === 'DISTRIBUTION' && (
              <TextField
                label="Distribution Type"
                value={formData.distribution_type || ''}
                onChange={e => handleInputChange('distribution_type', e.target.value)}
                select
              >
                <MenuItem value="INTEREST">Interest</MenuItem>
                <MenuItem value="DIVIDEND">Dividend</MenuItem>
                <MenuItem value="OTHER">Other</MenuItem>
              </TextField>
            )}
            {eventType === 'UNIT_PURCHASE' && (
              <>
                <TextField
                  label="Units Purchased"
                  type="number"
                  value={formData.units_purchased || ''}
                  onChange={e => handleInputChange('units_purchased', e.target.value)}
                  required
                />
                <TextField
                  label="Unit Price"
                  type="number"
                  value={formData.unit_price || ''}
                  onChange={e => handleInputChange('unit_price', e.target.value)}
                  required
                />
                <TextField
                  label="Brokerage Fee"
                  type="number"
                  value={formData.brokerage_fee || ''}
                  onChange={e => handleInputChange('brokerage_fee', e.target.value)}
                />
              </>
            )}
            {eventType === 'UNIT_SALE' && (
              <>
                <TextField
                  label="Units Sold"
                  type="number"
                  value={formData.units_sold || ''}
                  onChange={e => handleInputChange('units_sold', e.target.value)}
                  required
                />
                <TextField
                  label="Unit Price"
                  type="number"
                  value={formData.unit_price || ''}
                  onChange={e => handleInputChange('unit_price', e.target.value)}
                  required
                />
                <TextField
                  label="Brokerage Fee"
                  type="number"
                  value={formData.brokerage_fee || ''}
                  onChange={e => handleInputChange('brokerage_fee', e.target.value)}
                />
              </>
            )}
            <TextField
              label="Description"
              value={formData.description || ''}
              onChange={e => handleInputChange('description', e.target.value)}
              multiline
              minRows={2}
              maxRows={4}
            />
            <TextField
              label="Reference Number"
              value={formData.reference_number || ''}
              onChange={e => handleInputChange('reference_number', e.target.value)}
            />
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={submitting}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={submitting || !validate()}>
          {submitting ? <CircularProgress size={20} /> : 'Add Event'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateFundEventModal; 