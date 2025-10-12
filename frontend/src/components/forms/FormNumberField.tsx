/**
 * FormNumberField Component
 * 
 * Number field component that integrates React Hook Form with existing NumberInputField.
 * Preserves thousand separator formatting and focus/blur behavior.
 */

import React from 'react';
import { Controller, Control, FieldValues, Path } from 'react-hook-form';
import { NumberInputField } from '../ui/NumberInputField';

interface FormNumberFieldProps<T extends FieldValues> {
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
  
  /** Whether to allow decimal values */
  allowDecimals?: boolean;
  
  /** Whether to allow negative values */
  allowNegative?: boolean;
  
  /** Full width styling */
  fullWidth?: boolean;
}

/**
 * Number field with formatting, integrated with React Hook Form
 * Wraps existing NumberInputField component
 */
export function FormNumberField<T extends FieldValues>({
  name,
  control,
  label,
  required = false,
  helperText,
  allowDecimals = true,
  allowNegative = false,
  fullWidth = true
}: FormNumberFieldProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => {
        const showError = !!fieldState.error && fieldState.isTouched;
        
        return (
          <NumberInputField
            value={field.value || ''}
            onInputChange={(fieldName, value) => {
              field.onChange(value);
            }}
            fieldName={String(name)}
            label={
              <span>
                {label}
                {required && <span style={{ color: 'red' }}> *</span>}
              </span>
            }
            allowDecimals={allowDecimals}
            allowNegative={allowNegative}
            error={showError}
            helperText={
              showError
                ? fieldState.error?.message
                : helperText
            }
            fullWidth={fullWidth}
          />
        );
      }}
    />
  );
}

export default FormNumberField;

