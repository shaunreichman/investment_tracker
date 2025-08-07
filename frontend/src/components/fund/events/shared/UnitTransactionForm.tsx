import React from 'react';
import { TextField, Box, Typography } from '@mui/material';
import { formatNumber } from '../../../../utils/helpers';

interface UnitTransactionFormProps {
  eventType: 'UNIT_PURCHASE' | 'UNIT_SALE';
  formData: {
    units_purchased?: string;
    units_sold?: string;
    unit_price?: string;
    brokerage_fee?: string;
    amount?: string;
  };
  validationErrors: {
    units_purchased?: string;
    units_sold?: string;
    unit_price?: string;
    brokerage_fee?: string;
    amount?: string;
  };
  onInputChange: (field: string, value: string) => void;
}

const UnitTransactionForm: React.FC<UnitTransactionFormProps> = ({
  eventType,
  formData,
  validationErrors,
  onInputChange,
}) => {
  // Update amount when units, price, or brokerage changes
  React.useEffect(() => {
    const calculateAmount = () => {
      const units = eventType === 'UNIT_PURCHASE' 
        ? parseFloat(formData.units_purchased || '0')
        : parseFloat(formData.units_sold || '0');
      const unitPrice = parseFloat(formData.unit_price || '0');
      const brokerageFee = parseFloat(formData.brokerage_fee || '0');
      
      const totalAmount = (units * unitPrice) + brokerageFee;
      return totalAmount;
    };

    const amount = calculateAmount();
    if (amount > 0) {
      onInputChange('amount', amount.toString());
    }
  }, [formData.units_purchased, formData.units_sold, formData.unit_price, formData.brokerage_fee, eventType, onInputChange]);

  const isPurchase = eventType === 'UNIT_PURCHASE';
  const unitsField = isPurchase ? 'units_purchased' : 'units_sold';
  const unitsLabel = isPurchase ? 'Units Purchased' : 'Units Sold';

  return (
    <Box>
      <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
        {isPurchase ? 'Unit Purchase Details' : 'Unit Sale Details'}
      </Typography>
      
      <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr' }} gap={2}>
        <TextField
          label={<span>{unitsLabel} <span style={{ color: '#d32f2f' }}>*</span></span>}
          type="number"
          value={formData[unitsField] || ''}
          onChange={e => onInputChange(unitsField, e.target.value)}
          fullWidth
          error={!!validationErrors[unitsField]}
          helperText={validationErrors[unitsField]}
          inputProps={{
            min: 0,
            step: 'any'
          }}
        />
        
        <TextField
          label={<span>Unit Price <span style={{ color: '#d32f2f' }}>*</span></span>}
          type="number"
          value={formData.unit_price || ''}
          onChange={e => onInputChange('unit_price', e.target.value)}
          fullWidth
          error={!!validationErrors.unit_price}
          helperText={validationErrors.unit_price}
          inputProps={{
            min: 0,
            step: 'any'
          }}
        />
        
        <TextField
          label="Brokerage Fee (Optional)"
          type="number"
          value={formData.brokerage_fee || ''}
          onChange={e => onInputChange('brokerage_fee', e.target.value)}
          fullWidth
          error={!!validationErrors.brokerage_fee}
          helperText={validationErrors.brokerage_fee}
          inputProps={{
            min: 0,
            step: 'any'
          }}
        />
        
        <TextField
          label="Total Amount"
          type="text"
          value={formatNumber(formData.amount || '')}
          fullWidth
          disabled
          helperText={`Calculated: (${formData[unitsField] || 0} × ${formData.unit_price || 0}) + ${formData.brokerage_fee || 0}`}
        />
      </Box>
    </Box>
  );
};

export default UnitTransactionForm; 