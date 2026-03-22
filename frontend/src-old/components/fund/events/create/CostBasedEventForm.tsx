import React from 'react';
import { TextField, Box, Typography, useTheme } from '@mui/material';
import { NumberInputField } from '../../../shared/forms';

interface CostBasedEventFormProps {
  eventType: 'CAPITAL_CALL' | 'RETURN_OF_CAPITAL';
  formData: {
    event_date?: string;
    amount?: string;
    notes?: string;
  };
  validationErrors: {
    event_date?: string;
    amount?: string;
    notes?: string;
  };
  onInputChange: (field: string, value: string) => void;
}

const CostBasedEventForm: React.FC<CostBasedEventFormProps> = ({
  eventType,
  formData,
  validationErrors,
  onInputChange,
}) => {
  const theme = useTheme();
  
  const isCapitalCall = eventType === 'CAPITAL_CALL';
  const eventLabel = isCapitalCall ? 'Capital Call' : 'Capital Return';
  const amountLabel = isCapitalCall ? 'Call Amount' : 'Return Amount';

  return (
    <Box
      sx={{
        animation: 'fadeInUp 0.5s ease-out 0.1s both',
        '@keyframes fadeInUp': {
          '0%': {
            opacity: 0,
            transform: 'translateY(30px)',
          },
          '100%': {
            opacity: 1,
            transform: 'translateY(0)',
          }
        }
      }}
    >
      <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
        {eventLabel} Details
      </Typography>
      
      <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr' }} gap={2}>
        <TextField
          label={<span>Event Date <span style={{ color: theme.palette.error.main }}>*</span></span>}
          type="date"
          value={formData.event_date || ''}
          onChange={e => onInputChange('event_date', e.target.value)}
          InputLabelProps={{ shrink: true }}
          fullWidth
          error={!!validationErrors.event_date}
          helperText={validationErrors.event_date}
        />
        
        <NumberInputField
          label={<span>{amountLabel} <span style={{ color: theme.palette.error.main }}>*</span></span>}
          value={formData.amount || ''}
          onInputChange={onInputChange}
          fieldName="amount"
          allowDecimals={true}
          allowNegative={false}
          fullWidth
          error={!!validationErrors.amount}
          helperText={validationErrors.amount}
        />
        
        <TextField
          label="Notes (Optional)"
          type="text"
          value={formData.notes || ''}
          onChange={e => onInputChange('notes', e.target.value)}
          fullWidth
          multiline
          rows={3}
          error={!!validationErrors.notes}
          helperText={validationErrors.notes}
          sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}
        />
      </Box>
    </Box>
  );
};

export default CostBasedEventForm;
