import React from 'react';
import {
  TextField,
  MenuItem,
  Typography,
  Divider,
  Button,
  FormControlLabel,
  Checkbox,
  Box
} from '@mui/material';
import { formatNumber, parseNumber } from '../../../../utils/helpers';

interface TaxStatementFormProps {
  formData: any;
  validationErrors: any;
  financialYears: string[];
  fundEntity: any;
  hybridFieldOverrides: any;
  onInputChange: (field: string, value: string) => void;
  onHybridFieldToggle: (field: string) => void;
}

const TaxStatementForm: React.FC<TaxStatementFormProps> = ({
  formData = {},
  validationErrors = {},
  financialYears = [],
  fundEntity,
  hybridFieldOverrides = {},
  onInputChange,
  onHybridFieldToggle
}) => {
  return (
    <>
      {/* Basic Information */}
      <Typography variant="h6" color="primary" sx={{ mt: 2, mb: 1 }}>
        Basic Information
      </Typography>
      <TextField
        label="Entity"
        value={fundEntity?.name || 'Loading...'}
        disabled
        fullWidth
      />
      <TextField
        select
        label={<span>Financial Year <span style={{ color: '#d32f2f' }}>*</span></span>}
        value={formData.financial_year || ''}
        onChange={e => onInputChange('financial_year', e.target.value)}
        fullWidth
        error={!!validationErrors.financial_year}
        helperText={validationErrors.financial_year}
      >
        {financialYears.map((year) => (
          <MenuItem key={year} value={year}>
            {year}
          </MenuItem>
        ))}
      </TextField>
      <TextField
        label={<span>Statement Date <span style={{ color: '#d32f2f' }}>*</span></span>}
        type="date"
        value={formData.statement_date || ''}
        onChange={e => onInputChange('statement_date', e.target.value)}
        fullWidth
        error={!!validationErrors.statement_date}
        helperText={validationErrors.statement_date}
        InputLabelProps={{ shrink: true }}
      />
      <TextField
        label="Tax Payment Date"
        value={formData.tax_payment_date || ''}
        disabled
        fullWidth
        helperText="Auto-calculated as last day of financial year"
      />
      <TextField
        label={<span>End of Financial Year Debt Interest Deduction Rate (%) <span style={{ color: '#d32f2f' }}>*</span></span>}
        type="number"
        value={formData.eofy_debt_interest_deduction_rate || ''}
        onChange={e => onInputChange('eofy_debt_interest_deduction_rate', e.target.value)}
        fullWidth
        error={!!validationErrors.eofy_debt_interest_deduction_rate}
        helperText={validationErrors.eofy_debt_interest_deduction_rate}
      />
      
      <Divider sx={{ my: 2 }} />
      
      {/* Interest Income */}
      <Typography variant="h6" color="primary" sx={{ mb: 1 }}>
        Interest Income
      </Typography>
      
      <TextField
        label="Interest Received in Cash"
        type="number"
        value={formData.interest_received_in_cash || ''}
        onChange={e => onInputChange('interest_received_in_cash', e.target.value)}
        fullWidth
        error={!!validationErrors.interest_received_in_cash}
        helperText={validationErrors.interest_received_in_cash}
      />
      <TextField
        label="Interest Receivable This FY"
        type="number"
        value={formData.interest_receivable_this_fy || ''}
        onChange={e => onInputChange('interest_receivable_this_fy', e.target.value)}
        fullWidth
        error={!!validationErrors.interest_receivable_this_fy}
        helperText={validationErrors.interest_receivable_this_fy}
      />
      <TextField
        label="Interest Receivable Previous FY"
        type="number"
        value={formData.interest_receivable_prev_fy || ''}
        onChange={e => onInputChange('interest_receivable_prev_fy', e.target.value)}
        fullWidth
        error={!!validationErrors.interest_receivable_prev_fy}
        helperText={validationErrors.interest_receivable_prev_fy}
      />
      <TextField
        label="Interest Non-Resident Withholding Tax from Statement"
        type="number"
        value={formData.interest_non_resident_withholding_tax_from_statement || ''}
        onChange={e => onInputChange('interest_non_resident_withholding_tax_from_statement', e.target.value)}
        fullWidth
        error={!!validationErrors.interest_non_resident_withholding_tax_from_statement}
        helperText={validationErrors.interest_non_resident_withholding_tax_from_statement}
      />
      <TextField
        label="Interest Income Tax Rate (%)"
        type="number"
        value={formData.interest_income_tax_rate || ''}
        onChange={e => onInputChange('interest_income_tax_rate', e.target.value)}
        fullWidth
        error={!!validationErrors.interest_income_tax_rate}
        helperText={validationErrors.interest_income_tax_rate}
      />
      
      <Divider sx={{ my: 2 }} />
      
      {/* Dividend Income */}
      <Typography variant="h6" color="primary" sx={{ mb: 1 }}>
        Dividend Income
      </Typography>
      <TextField
        label="Dividend Franked Income Amount"
        type="number"
        value={formData.dividend_franked_income_amount || ''}
        onChange={e => onInputChange('dividend_franked_income_amount', e.target.value)}
        fullWidth
        error={!!validationErrors.dividend_franked_income_amount}
        helperText={validationErrors.dividend_franked_income_amount}
        InputProps={{
          endAdornment: (
            <Button
              size="small"
              variant={hybridFieldOverrides.dividend_franked_income_amount ? 'contained' : 'outlined'}
              onClick={() => onHybridFieldToggle('dividend_franked_income_amount')}
              sx={{ minWidth: 'auto', px: 1 }}
            >
              {hybridFieldOverrides.dividend_franked_income_amount ? 'Manual' : 'Auto'}
            </Button>
          )
        }}
      />
      <TextField
        label="Dividend Unfranked Income Amount"
        type="number"
        value={formData.dividend_unfranked_income_amount || ''}
        onChange={e => onInputChange('dividend_unfranked_income_amount', e.target.value)}
        fullWidth
        error={!!validationErrors.dividend_unfranked_income_amount}
        helperText={validationErrors.dividend_unfranked_income_amount}
        InputProps={{
          endAdornment: (
            <Button
              size="small"
              variant={hybridFieldOverrides.dividend_unfranked_income_amount ? 'contained' : 'outlined'}
              onClick={() => onHybridFieldToggle('dividend_unfranked_income_amount')}
              sx={{ minWidth: 'auto', px: 1 }}
            >
              {hybridFieldOverrides.dividend_unfranked_income_amount ? 'Manual' : 'Auto'}
            </Button>
          )
        }}
      />
      <TextField
        label="Dividend Franked Income Tax Rate (%)"
        type="number"
        value={formData.dividend_franked_income_tax_rate || ''}
        onChange={e => onInputChange('dividend_franked_income_tax_rate', e.target.value)}
        fullWidth
        error={!!validationErrors.dividend_franked_income_tax_rate}
        helperText={validationErrors.dividend_franked_income_tax_rate}
      />
      <TextField
        label="Dividend Unfranked Income Tax Rate (%)"
        type="number"
        value={formData.dividend_unfranked_income_tax_rate || ''}
        onChange={e => onInputChange('dividend_unfranked_income_tax_rate', e.target.value)}
        fullWidth
        error={!!validationErrors.dividend_unfranked_income_tax_rate}
        helperText={validationErrors.dividend_unfranked_income_tax_rate}
      />
      
      <Divider sx={{ my: 2 }} />
      
      {/* Capital Gains */}
      <Typography variant="h6" color="primary" sx={{ mb: 1 }}>
        Capital Gains
      </Typography>
      <TextField
        label="Capital Gain Income Amount"
        type="number"
        value={formData.capital_gain_income_amount || ''}
        onChange={e => onInputChange('capital_gain_income_amount', e.target.value)}
        fullWidth
        error={!!validationErrors.capital_gain_income_amount}
        helperText={validationErrors.capital_gain_income_amount}
        InputProps={{
          endAdornment: (
            <Button
              size="small"
              variant={hybridFieldOverrides.capital_gain_income_amount ? 'contained' : 'outlined'}
              onClick={() => onHybridFieldToggle('capital_gain_income_amount')}
              sx={{ minWidth: 'auto', px: 1 }}
            >
              {hybridFieldOverrides.capital_gain_income_amount ? 'Manual' : 'Auto'}
            </Button>
          )
        }}
      />
      <TextField
        label="Capital Gain Income Tax Rate (%)"
        type="number"
        value={formData.capital_gain_income_tax_rate || ''}
        onChange={e => onInputChange('capital_gain_income_tax_rate', e.target.value)}
        fullWidth
        error={!!validationErrors.capital_gain_income_tax_rate}
        helperText={validationErrors.capital_gain_income_tax_rate}
      />
      
      <Divider sx={{ my: 2 }} />
      
      {/* Additional Information */}
      <Typography variant="h6" color="primary" sx={{ mb: 1 }}>
        Additional Information
      </Typography>
      <TextField
        label="Accountant"
        value={formData.accountant || ''}
        onChange={e => onInputChange('accountant', e.target.value)}
        fullWidth
        error={!!validationErrors.accountant}
        helperText={validationErrors.accountant}
      />
      <TextField
        label="Notes"
        multiline
        rows={3}
        value={formData.notes || ''}
        onChange={e => onInputChange('notes', e.target.value)}
        fullWidth
        error={!!validationErrors.notes}
        helperText={validationErrors.notes}
      />
      <FormControlLabel
        control={
          <Checkbox
            checked={formData.non_resident || false}
            onChange={e => onInputChange('non_resident', e.target.checked.toString())}
          />
        }
        label="Non-Resident"
      />
    </>
  );
};

export default TaxStatementForm; 