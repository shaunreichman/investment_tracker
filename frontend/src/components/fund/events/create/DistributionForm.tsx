import React from 'react';
import { TextField, Box, Typography, FormControlLabel, Checkbox } from '@mui/material';
import { formatNumber, parseNumber } from '../../../../utils/helpers';
import { ValidationErrors, FormData } from '../../../../hooks/useEventForm';

interface DistributionFormProps {
  // Form state
  distributionType: string;
  subDistributionType: string;
  formData: FormData;
  validationErrors: ValidationErrors;
  
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
  // Only render for distribution events
  if (eventType !== 'DISTRIBUTION') {
    return null;
  }

  return (
    <>
      {/* Distribution Type Display */}
      <TextField
        label={<span>Distribution Type <span style={{ color: '#d32f2f' }}>*</span></span>}
        value={distributionType}
        disabled
        fullWidth
        error={!!validationErrors.distribution_type}
        helperText={validationErrors.distribution_type}
      />

      {/* Sub-Distribution Type Display */}
      {(distributionType === 'DIVIDEND' || distributionType === 'INTEREST') && (
        <TextField
          label={<span>Sub-Distribution Type <span style={{ color: '#d32f2f' }}>*</span></span>}
          value={subDistributionType}
          disabled
          fullWidth
          error={!!validationErrors.sub_distribution_type}
          helperText={validationErrors.sub_distribution_type}
        />
      )}

      {/* Simple Amount Field for all distributions */}
      <TextField
        label={<span>Amount <span style={{ color: '#d32f2f' }}>*</span></span>}
        type="text"
        value={formatNumber(formData.amount || '')}
        onChange={e => onInputChange('amount', parseNumber(e.target.value))}
        fullWidth
        error={!!validationErrors.amount}
        helperText={validationErrors.amount}
      />

      {/* Withholding Tax Checkbox for Interest distributions */}
      {distributionType === 'INTEREST' && (
        <FormControlLabel
          control={
            <Checkbox
              checked={formData.has_withholding_tax === true}
              onChange={(e) => onInputChange('has_withholding_tax', e.target.checked ? 'true' : 'false')}
            />
          }
          label="Has Withholding Tax"
        />
      )}

      {/* Withholding Tax Fields (only shown when checkbox is checked) */}
      {distributionType === 'INTEREST' && formData.has_withholding_tax === true && (
        <Box>
          <Typography variant="body2" color="text.secondary" mb={1}>
            Withholding Tax Details:
          </Typography>
          
          <TextField
            label="Withholding Tax Amount"
            type="text"
            value={formatNumber(formData.withholding_tax_amount || '')}
            onChange={e => onInputChange('withholding_tax_amount', parseNumber(e.target.value))}
            fullWidth
            error={!!validationErrors.withholding_tax_amount}
            helperText={validationErrors.withholding_tax_amount}
            sx={{ mb: 2 }}
          />
          
          <TextField
            label="Withholding Tax Rate (%)"
            type="text"
            value={formatNumber(formData.withholding_tax_rate || '')}
            onChange={e => onInputChange('withholding_tax_rate', parseNumber(e.target.value))}
            fullWidth
            error={!!validationErrors.withholding_tax_rate}
            helperText={validationErrors.withholding_tax_rate}
          />
        </Box>
      )}
    </>
  );
};

export default DistributionForm; 