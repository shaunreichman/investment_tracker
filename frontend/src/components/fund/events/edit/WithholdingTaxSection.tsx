import React from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  RadioGroup,
  FormControlLabel,
  Radio
} from '@mui/material';
import { validateField } from '../../../../utils/validators';
import { formatNumber, parseNumber } from '../../../../utils/helpers';

interface WithholdingTaxSectionProps {
  // Form data
  formData: any;
  setFormData: (data: any) => void;
  
  // State management
  interestType: 'regular' | 'withholding';
  setInterestType: (type: 'regular' | 'withholding') => void;
  withholdingAmountType: 'gross' | 'net' | '';
  setWithholdingAmountType: (type: 'gross' | 'net' | '') => void;
  withholdingTaxType: 'amount' | 'rate' | '';
  setWithholdingTaxType: (type: 'amount' | 'rate' | '') => void;
  
  // Validation
  validationErrors: any;
  setValidationErrors: (errors: any) => void;
  
  // Event info
  event: any;
  
  // Input handling
  handleInputChange: (field: string, value: string) => void;
}

const WithholdingTaxSection: React.FC<WithholdingTaxSectionProps> = ({
  formData,
  setFormData,
  interestType,
  setInterestType,
  withholdingAmountType,
  setWithholdingAmountType,
  withholdingTaxType,
  setWithholdingTaxType,
  validationErrors,
  setValidationErrors,
  event,
  handleInputChange
}) => {
  // Only render for interest distribution events
  if (event?.event_type !== 'DISTRIBUTION' || formData.distribution_type !== 'interest') {
    return null;
  }

  return (
    <>
      {/* Interest Type Selection */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Interest Type
        </Typography>
        <RadioGroup
          row
          value={interestType}
          onChange={(e) => setInterestType(e.target.value as 'regular' | 'withholding')}
        >
          <FormControlLabel
            value="regular"
            control={<Radio />}
            label="Regular Interest"
          />
          <FormControlLabel
            value="withholding"
            control={<Radio />}
            label="Withholding Tax Interest"
          />
        </RadioGroup>
      </Box>

      {/* Regular Interest Field */}
      {interestType === 'regular' && (
        <TextField
          fullWidth
          label="Gross Interest"
          type="number"
          value={formData.gross_interest || ''}
          onChange={(e) => handleInputChange('gross_interest', e.target.value)}
          error={!!validationErrors.gross_interest}
          helperText={validationErrors.gross_interest}
          sx={{ mb: 2 }}
        />
      )}
      
      {/* Withholding Tax Fields */}
      {interestType === 'withholding' && (
        <>
          {/* Amount Type Selection */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" mb={1}>
              Amount Type:
            </Typography>
            <Box display="flex" gap={1}>
              <Button
                size="small"
                variant={withholdingAmountType === 'gross' ? 'contained' : 'outlined'}
                onClick={() => setWithholdingAmountType('gross')}
              >
                Gross
              </Button>
              <Button
                size="small"
                variant={withholdingAmountType === 'net' ? 'contained' : 'outlined'}
                onClick={() => setWithholdingAmountType('net')}
              >
                Net
              </Button>
            </Box>
          </Box>

          {/* Tax Type Selection */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" mb={1}>
              Tax Type:
            </Typography>
            <Box display="flex" gap={1}>
              <Button
                size="small"
                variant={withholdingTaxType === 'amount' ? 'contained' : 'outlined'}
                onClick={() => setWithholdingTaxType('amount')}
              >
                Tax Amount
              </Button>
              <Button
                size="small"
                variant={withholdingTaxType === 'rate' ? 'contained' : 'outlined'}
                onClick={() => setWithholdingTaxType('rate')}
              >
                Tax Rate (%)
              </Button>
            </Box>
          </Box>

          {/* Amount Input Field */}
          {withholdingAmountType && (
            <TextField
              fullWidth
              label={`${withholdingAmountType === 'gross' ? 'Gross' : 'Net'} Interest`}
              type="number"
              value={formData[withholdingAmountType === 'gross' ? 'gross_interest' : 'net_interest'] || ''}
              onChange={(e) => handleInputChange(withholdingAmountType === 'gross' ? 'gross_interest' : 'net_interest', e.target.value)}
              error={!!validationErrors[withholdingAmountType === 'gross' ? 'gross_interest' : 'net_interest']}
              helperText={validationErrors[withholdingAmountType === 'gross' ? 'gross_interest' : 'net_interest']}
              sx={{ mb: 2 }}
            />
          )}

          {/* Tax Input Field */}
          {withholdingTaxType && (
            <TextField
              fullWidth
              label={withholdingTaxType === 'amount' ? 'Tax Amount' : 'Tax Rate (%)'}
              type="number"
              value={formData[withholdingTaxType === 'amount' ? 'withholding_amount' : 'withholding_rate'] || ''}
              onChange={(e) => handleInputChange(withholdingTaxType === 'amount' ? 'withholding_amount' : 'withholding_rate', e.target.value)}
              error={!!validationErrors[withholdingTaxType === 'amount' ? 'withholding_amount' : 'withholding_rate']}
              helperText={validationErrors[withholdingTaxType === 'amount' ? 'withholding_amount' : 'withholding_rate']}
              sx={{ mb: 2 }}
            />
          )}
        </>
      )}
    </>
  );
};

export default WithholdingTaxSection; 