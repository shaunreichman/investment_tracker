import React, { useState } from 'react';
import { 
  TextField, 
  Box, 
  Typography, 
  useTheme,
  ToggleButtonGroup,
  ToggleButton,
  InputAdornment
} from '@mui/material';
import { NumberInputField } from '../../../shared/forms';

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
  
  // State for toggle button selections
  const [amountType, setAmountType] = useState<'gross' | 'net'>('gross');
  const [taxType, setTaxType] = useState<'amount' | 'percentage'>('amount');
  
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
      </Box>

      {/* Withholding Tax Fields - Only show for Interest with Withholding Tax */}
      {distributionType === 'INTEREST' && subDistributionType === 'WITHHOLDING_TAX' && (
        <Box mt={3}>
          <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
            Withholding Tax Details
          </Typography>
          
          {/* Amount Type Selection */}
          <Box mb={3}>
            <Typography variant="subtitle2" mb={1} color="text.secondary">
              Amount Type <span style={{ color: theme.palette.error.main }}>*</span>
            </Typography>
            <ToggleButtonGroup 
              value={amountType} 
              exclusive 
              onChange={(_, value) => value && setAmountType(value)}
              sx={{ mb: 2 }}
            >
              <ToggleButton value="gross" sx={{ minWidth: 120 }}>
                Gross Amount
              </ToggleButton>
              <ToggleButton value="net" sx={{ minWidth: 120 }}>
                Net Amount
              </ToggleButton>
            </ToggleButtonGroup>
            
            {/* Conditional Amount Fields */}
            <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr' }} gap={2}>
              {amountType === 'gross' && (
                <NumberInputField
                  label={<span>Gross Interest Amount <span style={{ color: theme.palette.error.main }}>*</span></span>}
                  value={formData.interest_gross_amount || ''}
                  onInputChange={onInputChange}
                  fieldName="interest_gross_amount"
                  allowDecimals={true}
                  allowNegative={false}
                  fullWidth
                  error={!!validationErrors.interest_gross_amount}
                  helperText={validationErrors.interest_gross_amount}
                />
              )}
              
              {amountType === 'net' && (
                <NumberInputField
                  label={<span>Net Interest Amount <span style={{ color: theme.palette.error.main }}>*</span></span>}
                  value={formData.interest_net_amount || ''}
                  onInputChange={onInputChange}
                  fieldName="interest_net_amount"
                  allowDecimals={true}
                  allowNegative={false}
                  fullWidth
                  error={!!validationErrors.interest_net_amount}
                  helperText={validationErrors.interest_net_amount}
                />
              )}
            </Box>
          </Box>

          {/* Tax Type Selection */}
          <Box mb={3}>
            <Typography variant="subtitle2" mb={1} color="text.secondary">
              Tax Type <span style={{ color: theme.palette.error.main }}>*</span>
            </Typography>
            <ToggleButtonGroup 
              value={taxType} 
              exclusive 
              onChange={(_, value) => value && setTaxType(value)}
              sx={{ mb: 2 }}
            >
              <ToggleButton value="amount" sx={{ minWidth: 120 }}>
                Tax Amount
              </ToggleButton>
              <ToggleButton value="percentage" sx={{ minWidth: 120 }}>
                Tax Rate (%)
              </ToggleButton>
            </ToggleButtonGroup>
            
            {/* Conditional Tax Fields */}
            <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr' }} gap={2}>
              {taxType === 'amount' && (
                <NumberInputField
                  label={<span>Withholding Tax Amount <span style={{ color: theme.palette.error.main }}>*</span></span>}
                  value={formData.interest_withholding_tax_amount || ''}
                  onInputChange={onInputChange}
                  fieldName="interest_withholding_tax_amount"
                  allowDecimals={true}
                  allowNegative={false}
                  fullWidth
                  error={!!validationErrors.interest_withholding_tax_amount}
                  helperText={validationErrors.interest_withholding_tax_amount}
                />
              )}
              
              {taxType === 'percentage' && (
                <NumberInputField
                  label={<span>Withholding Tax Rate (%) <span style={{ color: theme.palette.error.main }}>*</span></span>}
                  value={formData.interest_withholding_tax_rate || ''}
                  onInputChange={onInputChange}
                  fieldName="interest_withholding_tax_rate"
                  allowDecimals={true}
                  allowNegative={false}
                  fullWidth
                  error={!!validationErrors.interest_withholding_tax_rate}
                  helperText={validationErrors.interest_withholding_tax_rate}
                  inputProps={{ min: 0, max: 100, step: 0.01 }}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <Typography variant="body2" color="text.secondary">
                          %
                        </Typography>
                      </InputAdornment>
                    )
                  }}
                />
              )}
            </Box>
          </Box>
        </Box>
      )}

      {/* Simple Amount Field for non-withholding tax distributions */}
      {distributionType === 'INTEREST' && subDistributionType !== 'WITHHOLDING_TAX' && (
        <Box mt={3}>
          <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
            Interest Details
          </Typography>
          
          <NumberInputField
            label={<span>Interest Amount <span style={{ color: theme.palette.error.main }}>*</span></span>}
            value={formData.amount || ''}
            onInputChange={onInputChange}
            fieldName="amount"
            allowDecimals={true}
            allowNegative={false}
            fullWidth
            error={!!validationErrors.amount}
            helperText={validationErrors.amount}
          />
        </Box>
      )}

      {/* Simple Amount Field for Dividend and Other distributions */}
      {(distributionType === 'DIVIDEND' || distributionType === 'OTHER') && (
        <Box mt={3}>
          <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
            {distributionType === 'DIVIDEND' ? 'Dividend' : 'Distribution'} Details
          </Typography>
          
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
        </Box>
      )}
    </Box>
  );
};

export default DistributionForm; 