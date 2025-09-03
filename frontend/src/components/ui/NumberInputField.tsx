import React from 'react';
import { TextField, TextFieldProps } from '@mui/material';
import { useNumberInput } from '../../hooks';

interface NumberInputFieldProps extends Omit<TextFieldProps, 'onChange' | 'onBlur' | 'onFocus'> {
  value: string;
  onInputChange: (field: string, value: string) => void;
  fieldName: string;
  allowDecimals?: boolean;
  allowNegative?: boolean;
  locale?: string;
}

/**
 * Reusable NumberInputField component that provides consistent number input behavior
 * 
 * Features:
 * - Thousand separators on blur
 * - Clean input on focus
 * - Proper validation
 * - Consistent styling
 * - Enterprise-grade architecture
 * 
 * Usage:
 * <NumberInputField
 *   label="Amount"
 *   value={formData.amount}
 *   onInputChange={onInputChange}
 *   fieldName="amount"
 *   allowDecimals={true}
 *   allowNegative={false}
 *   required
 *   fullWidth
 * />
 */
export const NumberInputField: React.FC<NumberInputFieldProps> = ({
  value,
  onInputChange,
  fieldName,
  allowDecimals = true,
  allowNegative = false,
  locale = 'en-AU',
  ...textFieldProps
}) => {
  const numberInput = useNumberInput(value, {
    allowDecimals,
    allowNegative,
    locale
  });

  // Handle value changes from the number input hook
  const handleValueChange = (newValue: string) => {
    // Always pass the raw numeric value to the form, not the formatted display value
    const rawValue = numberInput.numericValue.toString();
    
    // Only update when the raw value actually changes
    if (rawValue !== value) {
      onInputChange(fieldName, rawValue);
    }
  };

  return (
    <TextField
      {...textFieldProps}
      type="text"
      value={numberInput.value}
      onChange={e => {
        const newValue = e.target.value;
        numberInput.onChange(newValue);
        handleValueChange(newValue);
      }}
      onBlur={() => {
        numberInput.onBlur();
        // Sync the formatted value back to form if needed
        if (numberInput.value !== value) {
          handleValueChange(numberInput.value);
        }
      }}
      onFocus={numberInput.onFocus}
      inputProps={{
        style: { textAlign: 'left' },
        ...textFieldProps.inputProps
      }}
    />
  );
};
