import React from 'react';
import { TextField, Box, Typography, FormControlLabel, Checkbox, useTheme } from '@mui/material';
import { NumberInputField } from '../../../ui/NumberInputField';

interface DistributionFormProps {
  // Form state
  distributionType: string;
  subDistributionType: string;
  formData: any;
  validationErrors: any;
  
  // Event handlers
  onInputChange: (field: string, value: string) => void;
  
  // Event type for context
  eventType: string;
}

const DistributionForm: React.FC<DistributionFormProps> = ({
  distributionType,
  subDistributionType,
  formData,
  validationErrors,
  onInputChange,
  eventType,
}) => {
  const theme = useTheme();
  
  // Only render for distribution events
  if (eventType !== 'DISTRIBUTION') {
    return null;
  }

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
        Distribution Details
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

        {/* Distribution Type Display */}
        <TextField
          label={<span>Distribution Type <span style={{ color: theme.palette.error.main }}>*</span></span>}
          value={distributionType}
          disabled
          fullWidth
          error={!!validationErrors.distribution_type}
          helperText={validationErrors.distribution_type}
        />

        {/* Sub-Distribution Type Display */}
        {(distributionType === 'DIVIDEND' || distributionType === 'INTEREST') && (
          <TextField
            label={<span>Sub-Distribution Type <span style={{ color: theme.palette.error.main }}>*</span></span>}
            value={subDistributionType}
            disabled
            fullWidth
            error={!!validationErrors.sub_distribution_type}
            helperText={validationErrors.sub_distribution_type}
          />
        )}

        {/* Simple Amount Field for all distributions */}
        <NumberInputField
          label={<span>Amount <span style={{ color: theme.palette.error.main }}>*</span></span>}
          value={formData.amount || ''}
          onInputChange={onInputChange}
          fieldName="amount"
          allowDecimals={true}
          allowNegative={false}
          fullWidth
          error={!!validationErrors.amount}
          helperText={validationErrors.amount}
        />

        {/* Notes Field */}
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

        {/* Withholding Tax Fields (only shown when Withholding Tax sub-type is selected) */}
        {distributionType === 'INTEREST' && subDistributionType === 'WITHHOLDING_TAX' && (
          <Box sx={{ gridColumn: { xs: '1', sm: '1 / -1' } }}>
            <Typography variant="body2" color="text.secondary" mb={1}>
              Withholding Tax Details:
            </Typography>
            
            <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr' }} gap={2}>
              <NumberInputField
                label="Withholding Tax Amount"
                value={formData.withholding_tax_amount || ''}
                onInputChange={onInputChange}
                fieldName="withholding_tax_amount"
                allowDecimals={true}
                allowNegative={false}
                fullWidth
                error={!!validationErrors.withholding_tax_amount}
                helperText={validationErrors.withholding_tax_amount}
              />
              
              <NumberInputField
                label="Withholding Tax Rate (%)"
                value={formData.withholding_tax_rate || ''}
                onInputChange={onInputChange}
                fieldName="withholding_tax_rate"
                allowDecimals={true}
                allowNegative={false}
                fullWidth
                error={!!validationErrors.withholding_tax_rate}
                helperText={validationErrors.withholding_tax_rate}
              />
            </Box>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default DistributionForm; 