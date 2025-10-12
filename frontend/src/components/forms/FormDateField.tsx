/**
 * FormDateField Component
 * 
 * Standardized date field component for React Hook Form integration.
 * Uses Material-UI TextField with type="date" for native date picker.
 */

import React from 'react';
import { TextField, TextFieldProps } from '@mui/material';
import { Controller, Control, FieldValues, Path } from 'react-hook-form';

interface FormDateFieldProps<T extends FieldValues> {
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
  
  /** Full width styling */
  fullWidth?: boolean;
  
  /** Additional Material-UI TextField props */
  textFieldProps?: Omit<TextFieldProps, 'name' | 'label' | 'error' | 'helperText' | 'type'>;
}

/**
 * Standardized date field with React Hook Form integration
 * Uses native browser date picker via TextField type="date"
 */
export function FormDateField<T extends FieldValues>({
  name,
  control,
  label,
  required = false,
  helperText,
  fullWidth = true,
  textFieldProps = {}
}: FormDateFieldProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => {
        const showError = !!fieldState.error && fieldState.isTouched;
        
        return (
          <TextField
            {...field}
            {...textFieldProps}
            type="date"
            label={
              <span>
                {label}
                {required && <span style={{ color: 'red' }}> *</span>}
              </span>
            }
            error={showError}
            helperText={
              showError
                ? fieldState.error?.message
                : helperText
            }
            InputLabelProps={{ 
              shrink: true,
              ...textFieldProps.InputLabelProps 
            }}
            fullWidth={fullWidth}
          />
        );
      }}
    />
  );
}

export default FormDateField;

