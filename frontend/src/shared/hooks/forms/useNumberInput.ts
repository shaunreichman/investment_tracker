/**
 * Number Input Hook
 * 
 * Reusable hook for handling number input fields with thousand separators.
 * Provides formatted display with raw numeric value access.
 * 
 * Features:
 * - Allows typing with thousand separators
 * - Removes separators when parsing
 * - Only allows valid number input
 * - Formats with thousand separators on blur
 * - Removes formatting on focus for easier editing
 * 
 * @example
 * ```typescript
 * const numberInput = useNumberInput('1234.56', {
 *   allowDecimals: true,
 *   allowNegative: false,
 *   locale: 'en-AU'
 * });
 * 
 * <TextField
 *   value={numberInput.value}
 *   onChange={e => numberInput.onChange(e.target.value)}
 *   onBlur={numberInput.onBlur}
 *   onFocus={numberInput.onFocus}
 * />
 * ```
 */

import { useState, useCallback } from 'react';

export interface UseNumberInputOptions {
  /** Whether to allow decimal values (default: true) */
  allowDecimals?: boolean;
  /** Whether to allow negative values (default: false) */
  allowNegative?: boolean;
  /** Locale string for number formatting (default: 'en-AU') */
  locale?: string;
}

export interface UseNumberInputReturn {
  /** Current display value (may include formatting) */
  value: string;
  /** Handler for value changes - validates and updates value */
  onChange: (inputValue: string) => string;
  /** Handler for blur event - formats value with thousand separators */
  onBlur: () => string;
  /** Handler for focus event - removes formatting for easier editing */
  onFocus: () => string;
  /** Reset the value to a new initial value */
  reset: (newValue?: string) => void;
  /** Raw numeric value (always unformatted number) */
  numericValue: number;
}

/**
 * Hook for managing number input with formatting
 * 
 * @param initialValue - Initial numeric value as string
 * @param options - Configuration options
 * @returns Object with value, handlers, and numeric value
 */
export const useNumberInput = (
  initialValue: string = '',
  options: UseNumberInputOptions = {}
): UseNumberInputReturn => {
  const {
    allowDecimals = true,
    allowNegative = false,
    locale = 'en-AU'
  } = options;

  const [value, setValue] = useState(initialValue);

  const handleChange = useCallback((inputValue: string) => {
    // Remove existing separators and parse
    const cleanValue = inputValue.replace(/,/g, '');
    
    // Build regex pattern based on options
    let pattern: string;
    if (allowDecimals && allowNegative) {
      pattern = '^-?\\d*\\.?\\d*$';
    } else if (allowDecimals) {
      pattern = '^\\d*\\.?\\d*$';
    } else if (allowNegative) {
      pattern = '^-?\\d*$';
    } else {
      pattern = '^\\d*$';
    }
    
    // Only allow valid number input
    if (cleanValue === '' || new RegExp(pattern).test(cleanValue)) {
      setValue(cleanValue);
      return cleanValue;
    }
    
    return value; // Return current value if input is invalid
  }, [value, allowDecimals, allowNegative]);

  const handleBlur = useCallback(() => {
    // Format with thousand separators when leaving the field
    if (value) {
      const num = parseFloat(value);
      if (!isNaN(num)) {
        const formatted = new Intl.NumberFormat(locale).format(num);
        setValue(formatted);
        return formatted;
      }
    }
    return value;
  }, [value, locale]);

  const handleFocus = useCallback(() => {
    // Remove formatting when entering the field for easier editing
    if (value) {
      const num = parseFloat(value.replace(/,/g, ''));
      if (!isNaN(num)) {
        const unformatted = num.toString();
        setValue(unformatted);
        return unformatted;
      }
    }
    return value;
  }, [value]);

  // Helper to get numeric value (always raw, no formatting)
  const getNumericValue = useCallback(() => {
    if (!value) return 0;
    const cleanValue = value.replace(/,/g, '');
    const num = parseFloat(cleanValue);
    return isNaN(num) ? 0 : num;
  }, [value]);

  const reset = useCallback((newValue: string = '') => {
    setValue(newValue);
  }, []);

  return {
    value,
    onChange: handleChange,
    onBlur: handleBlur,
    onFocus: handleFocus,
    reset,
    // Helper to get numeric value
    numericValue: getNumericValue()
  };
};

