import React from 'react';
import { TextField, Box, Typography, useTheme } from '@mui/material';
import { NumberInputField } from '../../../shared/forms';

interface UnitTransactionFormProps {
  eventType: 'UNIT_PURCHASE' | 'UNIT_SALE';
  formData: {
    event_date?: string;
    units_purchased?: string;
    units_sold?: string;
    unit_price?: string;
    brokerage_fee?: string;
    amount?: string;
    description?: string;
  };
  validationErrors: {
    event_date?: string;
    units_purchased?: string;
    units_sold?: string;
    unit_price?: string;
    brokerage_fee?: string;
    amount?: string;
    description?: string;
  };
  onInputChange: (field: string, value: string) => void;
}

const UnitTransactionForm: React.FC<UnitTransactionFormProps> = ({
  eventType,
  formData,
  validationErrors,
  onInputChange,
}) => {
  const theme = useTheme();
  
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
        {isPurchase ? 'Unit Purchase Details' : 'Unit Sale Details'}
      </Typography>
      
      <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr' }} gap={2}>
        <TextField
          label={<span>Event Date <span style={{ color: theme.palette.error.main }}>*</span></span>}
          type="date"
          value={formData.event_date || ''}
          onChange={(e) => onInputChange('event_date', e.target.value)}
          fullWidth
          error={!!validationErrors.event_date}
          helperText={validationErrors.event_date}
          InputLabelProps={{ shrink: true }}
        />
        
        <TextField
          label="Description (Optional)"
          value={formData.description || ''}
          onChange={(e) => onInputChange('description', e.target.value)}
          fullWidth
          error={!!validationErrors.description}
          helperText={validationErrors.description}
        />
        
        <NumberInputField
          label={<span>{unitsLabel} <span style={{ color: theme.palette.error.main }}>*</span></span>}
          value={formData[unitsField] || ''}
          onInputChange={onInputChange}
          fieldName={unitsField}
          allowDecimals={true}
          allowNegative={false}
          fullWidth
          error={!!validationErrors[unitsField]}
          helperText={validationErrors[unitsField]}
        />
        
        <NumberInputField
          label={<span>Unit Price <span style={{ color: theme.palette.error.main }}>*</span></span>}
          value={formData.unit_price || ''}
          onInputChange={onInputChange}
          fieldName="unit_price"
          allowDecimals={true}
          allowNegative={false}
          fullWidth
          error={!!validationErrors.unit_price}
          helperText={validationErrors.unit_price}
        />
        
        <NumberInputField
          label="Brokerage Fee (Optional)"
          value={formData.brokerage_fee || ''}
          onInputChange={onInputChange}
          fieldName="brokerage_fee"
          allowDecimals={true}
          allowNegative={false}
          fullWidth
          error={!!validationErrors.brokerage_fee}
          helperText={validationErrors.brokerage_fee}
        />
        
        <TextField
          label="Total Amount"
          type="text"
          value={formData.amount || ''}
          fullWidth
          disabled
          helperText={`Calculated: (${formData[unitsField] || 0} × ${formData.unit_price || 0}) + ${formData.brokerage_fee || 0}`}
        />
      </Box>
    </Box>
  );
};

export default UnitTransactionForm; 