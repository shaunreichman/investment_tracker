/**
 * FormSelectField Component
 * 
 * Standardized select/dropdown field component for React Hook Form integration.
 * Implements consistent validation display rules.
 */

import React from 'react';
import { 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  FormHelperText,
  SelectProps 
} from '@mui/material';
import { Controller, Control, FieldValues, Path } from 'react-hook-form';
import type { SelectOption } from './types';
import { shouldShowError, getFieldLabel, getHelperText, getFieldColor } from './utils';

interface FormSelectFieldProps<T extends FieldValues> {
  /** Field name from the form schema */
  name: Path<T>;
  
  /** React Hook Form control instance */
  control: Control<T>;
  
  /** Display label for the field */
  label: string;
  
  /** Options for the select dropdown */
  options: SelectOption[];
  
  /** Whether this field is required */
  required?: boolean;
  
  /** Helper text shown when field has no error or not yet touched */
  helperText?: string;
  
  /** Full width styling */
  fullWidth?: boolean;
  
  /** Additional Material-UI Select props */
  selectProps?: Omit<SelectProps, 'name' | 'label' | 'error' | 'value' | 'onChange'>;
}

/**
 * Standardized select field with React Hook Form integration
 * Follows enterprise validation display rules
 */
export function FormSelectField<T extends FieldValues>({
  name,
  control,
  label,
  options,
  required = false,
  helperText,
  fullWidth = true,
  selectProps = {}
}: FormSelectFieldProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <FormControl 
          fullWidth={fullWidth} 
          error={shouldShowError(fieldState)}
          color={getFieldColor(fieldState, required)}
        >
          <InputLabel id={`${String(name)}-label`}>
            {label}
            {required && <span style={{ color: 'red' }}> *</span>}
          </InputLabel>
          <Select
            {...field}
            {...selectProps}
            labelId={`${String(name)}-label`}
            id={String(name)}
            label={
              <>
                {label}
                {required && <span style={{ color: 'red' }}> *</span>}
              </>
            }
          >
            {options.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
          <FormHelperText>
            {getHelperText(fieldState, helperText)}
          </FormHelperText>
        </FormControl>
      )}
    />
  );
}

export default FormSelectField;

