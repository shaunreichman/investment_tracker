/**
 * Number Input Field Component
 * 
 * Reusable controlled number input component that provides consistent number input behavior
 * with thousand separators, formatting, and validation.
 * 
 * Features:
 * - Thousand separators on blur
 * - Clean input on focus for easier editing
 * - Proper validation based on allowDecimals and allowNegative props
 * - Consistent styling
 * - Enterprise-grade architecture
 * 
 * @example
 * ```typescript
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
 * ```
 */

import React from 'react';
import { TextField, TextFieldProps } from '@mui/material';
import { useNumberInput } from '@/shared/hooks/forms';

export interface NumberInputFieldProps extends Omit<TextFieldProps, 'onChange' | 'onBlur' | 'onFocus'> {
  /** Current value (raw numeric string, no formatting) */
  value: string;
  /** Callback when value changes - receives field name and raw numeric value */
  onInputChange: (field: string, value: string) => void;
  /** Field name to pass to onInputChange callback */
  fieldName: string;
  /** Whether to allow decimal values (default: true) */
  allowDecimals?: boolean;
  /** Whether to allow negative values (default: false) */
  allowNegative?: boolean;
  /** Locale string for number formatting (default: 'en-AU') */
  locale?: string;
}

/**
 * NumberInputField component
 * 
 * Controlled component that manages number input with formatting.
 * Handles display formatting while maintaining raw numeric values for form state.
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

