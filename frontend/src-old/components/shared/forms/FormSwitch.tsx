/**
 * FormSwitch Component
 * 
 * Toggle switch component for React Hook Form integration.
 * Used for boolean fields with a more prominent on/off indicator.
 */

import React from 'react';
import { FormControlLabel, Switch, FormHelperText, Box } from '@mui/material';
import { Controller, Control, FieldValues, Path } from 'react-hook-form';
import { shouldShowError, getHelperText } from './utils';

interface FormSwitchProps<T extends FieldValues> {
  /** Field name from the form schema */
  name: Path<T>;
  
  /** React Hook Form control instance */
  control: Control<T>;
  
  /** Display label for the switch */
  label: string;
  
  /** Whether this field is required */
  required?: boolean;
  
  /** Helper text shown when field has no error or not yet touched */
  helperText?: string;
  
  /** Whether the switch is disabled */
  disabled?: boolean;
  
  /** Label placement relative to the switch */
  labelPlacement?: 'end' | 'start' | 'top' | 'bottom';
}

/**
 * Standardized toggle switch with React Hook Form integration
 * Follows enterprise validation display rules
 */
export function FormSwitch<T extends FieldValues>({
  name,
  control,
  label,
  required = false,
  helperText,
  disabled = false,
  labelPlacement = 'end'
}: FormSwitchProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <Box>
          <FormControlLabel
            control={
              <Switch
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
            labelPlacement={labelPlacement}
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

export default FormSwitch;

