/**
 * FormTextField Component
 * 
 * Standardized text field component for React Hook Form integration.
 * Implements consistent validation display rules:
 * - Red asterisk for required fields (always visible)
 * - Red outline when field has error AND is touched
 * - Error message when field has error AND is touched
 * - Helper text when NO error OR field not touched
 */

import React from 'react';
import { TextField, TextFieldProps } from '@mui/material';
import { Controller, Control, FieldValues, Path } from 'react-hook-form';
import { shouldShowError, getFieldLabel, getHelperText, getFieldColor } from './utils';

interface FormTextFieldProps<T extends FieldValues> {
  /** Field name from the form schema */
  name: Path<T>;
  
  /** React Hook Form control instance */
  control: Control<T>;
  
  /** Display label for the field */
  label: string;
  
  /** Whether this field is required */
  required?: boolean;
  
  /** Helper text shown when field has no error or not yet touched */
  helperText?: string;
  
  /** Additional Material-UI TextField props */
  textFieldProps?: Omit<TextFieldProps, 'name' | 'label' | 'error' | 'helperText'>;
}

/**
 * Standardized text field with React Hook Form integration
 * Follows enterprise validation display rules
 */
export function FormTextField<T extends FieldValues>({
  name,
  control,
  label,
  required = false,
  helperText,
  textFieldProps = {}
}: FormTextFieldProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <TextField
          {...field}
          {...textFieldProps}
          label={getFieldLabel(label, required)}
          color={getFieldColor(fieldState, required)}
          error={shouldShowError(fieldState)}
          helperText={getHelperText(fieldState, helperText)}
          fullWidth
        />
      )}
    />
  );
}

export default FormTextField;

