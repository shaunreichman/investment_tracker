import React from 'react';
import { TextField, TextFieldProps } from '@mui/material';
import { useNumberInput } from '../../hooks/useNumberInput';

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

  // Sync the hook value with the form when it changes
  React.useEffect(() => {
    if (numberInput.value !== value) {
      onInputChange(fieldName, numberInput.value);
    }
  }, [numberInput.value, value, onInputChange, fieldName]);

  return (
    <TextField
      {...textFieldProps}
      type="text"
      value={numberInput.value}
      onChange={e => numberInput.onChange(e.target.value)}
      onBlur={numberInput.onBlur}
      onFocus={numberInput.onFocus}
      inputProps={{
        style: { textAlign: 'left' },
        ...textFieldProps.inputProps
      }}
    />
  );
};
