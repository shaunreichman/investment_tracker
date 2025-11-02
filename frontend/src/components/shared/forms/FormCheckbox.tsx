/**
 * FormCheckbox Component
 * 
 * Single checkbox component for React Hook Form integration.
 * Used for boolean fields with clear label association.
 */

import React from 'react';
import { FormControlLabel, Checkbox, FormHelperText, Box } from '@mui/material';
import { Controller, Control, FieldValues, Path } from 'react-hook-form';
import { shouldShowError, getHelperText } from './utils';

interface FormCheckboxProps<T extends FieldValues> {
  /** Field name from the form schema */
  name: Path<T>;
  
  /** React Hook Form control instance */
  control: Control<T>;
  
  /** Display label for the checkbox */
  label: string;
  
  /** Whether this field is required */
  required?: boolean;
  
  /** Helper text shown when field has no error or not yet touched */
  helperText?: string;
  
  /** Whether the checkbox is disabled */
  disabled?: boolean;
}

/**
 * Standardized checkbox with React Hook Form integration
 * Follows enterprise validation display rules
 */
export function FormCheckbox<T extends FieldValues>({
  name,
  control,
  label,
  required = false,
  helperText,
  disabled = false
}: FormCheckboxProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <Box>
          <FormControlLabel
            control={
              <Checkbox
                {...field}
                checked={field.value || false}
                onChange={(e) => field.onChange(e.target.checked)}
                disabled={disabled}
              />
            }
            label={
              <span>
                {label}
                {required && <span style={{ color: 'red' }}> *</span>}
              </span>
            }
          />
          {(shouldShowError(fieldState) || helperText) && (
            <FormHelperText error={shouldShowError(fieldState)}>
              {getHelperText(fieldState, helperText)}
            </FormHelperText>
          )}
        </Box>
      )}
    />
  );
}

export default FormCheckbox;

