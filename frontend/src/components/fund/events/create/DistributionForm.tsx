import React from 'react';
import {
  TextField,
  Box,
  Button,
  Typography,
} from '@mui/material';
import { formatNumber, parseNumber } from '../../../../utils/helpers';
import { ValidationErrors, FormData } from '../../../../hooks/useEventForm';

interface DistributionFormProps {
  // Form state
  distributionType: string;
  subDistributionType: string;
  formData: FormData;
  validationErrors: ValidationErrors;
  
  // Withholding tax state
  withholdingAmountType: 'gross' | 'net' | '';
  withholdingTaxType: 'amount' | 'rate' | '';
  hybridFieldOverrides: { [key: string]: boolean };
  
  // Event handlers
  onInputChange: (field: string, value: string) => void;
  onWithholdingAmountTypeChange: (type: 'gross' | 'net' | '') => void;
  onWithholdingTaxTypeChange: (type: 'amount' | 'rate' | '') => void;
  onHybridFieldToggle: (field: string) => void;
  
  // Event type for context
  eventType: string;
}

const DistributionForm: React.FC<DistributionFormProps> = ({
  distributionType,
  subDistributionType,
  formData,
  validationErrors,
  withholdingAmountType,
  withholdingTaxType,
  hybridFieldOverrides,
  onInputChange,
  onWithholdingAmountTypeChange,
  onWithholdingTaxTypeChange,
  onHybridFieldToggle,
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

      {/* Regular Amount Field (for non-withholding tax distributions) */}
      {!(distributionType === 'INTEREST' && subDistributionType === 'WITHHOLDING_TAX') && (
        <TextField
          label={<span>Amount <span style={{ color: '#d32f2f' }}>*</span></span>}
          type="text"
          value={formatNumber(formData.amount || '')}
          onChange={e => onInputChange('amount', parseNumber(e.target.value))}
          fullWidth
          error={!!validationErrors.amount}
          helperText={validationErrors.amount}
        />
      )}

      {/* Withholding Tax Form Section */}
      {distributionType === 'INTEREST' && subDistributionType === 'WITHHOLDING_TAX' && (
        <>
          {/* Amount Type Selection */}
          <Box>
            <Typography variant="body2" color="text.secondary" mb={1}>
              Amount Type:
            </Typography>
            <Box display="flex" gap={1}>
              <Button
                size="small"
                variant={withholdingAmountType === 'gross' ? 'contained' : 'outlined'}
                onClick={() => onWithholdingAmountTypeChange('gross')}
              >
                Gross
              </Button>
              <Button
                size="small"
                variant={withholdingAmountType === 'net' ? 'contained' : 'outlined'}
                onClick={() => onWithholdingAmountTypeChange('net')}
              >
                Net
              </Button>
            </Box>
          </Box>

          {/* Tax Type Selection */}
          <Box>
            <Typography variant="body2" color="text.secondary" mb={1}>
              Tax Type:
            </Typography>
            <Box display="flex" gap={1}>
              <Button
                size="small"
                variant={withholdingTaxType === 'amount' ? 'contained' : 'outlined'}
                onClick={() => onWithholdingTaxTypeChange('amount')}
              >
                Tax Amount
              </Button>
              <Button
                size="small"
                variant={withholdingTaxType === 'rate' ? 'contained' : 'outlined'}
                onClick={() => onWithholdingTaxTypeChange('rate')}
              >
                Tax Rate (%)
              </Button>
            </Box>
          </Box>

          {/* Withholding Tax Input Fields */}
          {withholdingAmountType && (
            <TextField
              label={`${withholdingAmountType === 'gross' ? 'Gross' : 'Net'} Amount`}
              type="text"
              value={formatNumber(formData[withholdingAmountType === 'gross' ? 'gross_amount' : 'net_amount'] || '')}
              onChange={e => onInputChange(withholdingAmountType === 'gross' ? 'gross_amount' : 'net_amount', parseNumber(e.target.value))}
              fullWidth
              error={!!validationErrors[withholdingAmountType === 'gross' ? 'gross_amount' : 'net_amount']}
              helperText={validationErrors[withholdingAmountType === 'gross' ? 'gross_amount' : 'net_amount']}
            />
          )}

          {withholdingTaxType && (
            <TextField
              label={withholdingTaxType === 'amount' ? 'Tax Amount' : 'Tax Rate (%)'}
              type="text"
              value={formatNumber(formData[withholdingTaxType === 'amount' ? 'withholding_tax_amount' : 'withholding_tax_rate'] || '')}
              onChange={e => onInputChange(withholdingTaxType === 'amount' ? 'withholding_tax_amount' : 'withholding_tax_rate', parseNumber(e.target.value))}
              fullWidth
              error={!!validationErrors[withholdingTaxType === 'amount' ? 'withholding_tax_amount' : 'withholding_tax_rate']}
              helperText={validationErrors[withholdingTaxType === 'amount' ? 'withholding_tax_amount' : 'withholding_tax_rate']}
            />
          )}
        </>
      )}
    </>
  );
};

export default DistributionForm; 