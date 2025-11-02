/**
 * FormTextArea Component
 * 
 * Multi-line text area component for React Hook Form integration.
 * Implements consistent validation display rules.
 */

import React from 'react';
import { TextField, TextFieldProps } from '@mui/material';
import { Controller, Control, FieldValues, Path } from 'react-hook-form';
import { shouldShowError, getFieldLabel, getHelperText, getFieldColor } from './utils';

interface FormTextAreaProps<T extends FieldValues> {
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
  
  /** Number of rows to display */
  rows?: number;
  
  /** Minimum number of rows */
  minRows?: number;
  
  /** Maximum number of rows */
  maxRows?: number;
  
  /** Placeholder text */
  placeholder?: string;
  
  /** Additional Material-UI TextField props */
  textFieldProps?: Omit<TextFieldProps, 'name' | 'label' | 'error' | 'helperText' | 'multiline' | 'rows' | 'minRows' | 'maxRows'>;
}

/**
 * Standardized multi-line text area with React Hook Form integration
 * Follows enterprise validation display rules
 */
export function FormTextArea<T extends FieldValues>({
  name,
  control,
  label,
  required = false,
  helperText,
  rows = 4,
  minRows,
  maxRows,
  placeholder,
  textFieldProps = {}
}: FormTextAreaProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => {
        // Build props object conditionally to satisfy exactOptionalPropertyTypes
        const textareaProps: any = {
          ...field,
          ...textFieldProps,
          multiline: true,
          rows,
          label: getFieldLabel(label, required),
          color: getFieldColor(fieldState, required),
          error: shouldShowError(fieldState),
          helperText: getHelperText(fieldState, helperText),
          fullWidth: true
        };
        
        if (minRows !== undefined) {
          textareaProps.minRows = minRows;
        }
        if (maxRows !== undefined) {
          textareaProps.maxRows = maxRows;
        }
        if (placeholder !== undefined) {
          textareaProps.placeholder = placeholder;
        }
        
        return <TextField {...textareaProps} />;
      }}
    />
  );
}

export default FormTextArea;

