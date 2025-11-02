/**
 * FormRadioGroup Component
 * 
 * Radio button group component for React Hook Form integration.
 * Used for selecting one option from a predefined list.
 */

import React from 'react';
import { 
  FormControl, 
  FormLabel, 
  RadioGroup, 
  FormControlLabel, 
  Radio, 
  FormHelperText 
} from '@mui/material';
import { Controller, Control, FieldValues, Path } from 'react-hook-form';
import type { RadioOption } from './types';
import { shouldShowError, getHelperText } from './utils';

interface FormRadioGroupProps<T extends FieldValues> {
  /** Field name from the form schema */
  name: Path<T>;
  
  /** React Hook Form control instance */
  control: Control<T>;
  
  /** Display label for the radio group */
  label: string;
  
  /** Radio button options */
  options: RadioOption[];
  
  /** Whether this field is required */
  required?: boolean;
  
  /** Helper text shown when field has no error or not yet touched */
  helperText?: string;
  
  /** Layout direction */
  row?: boolean;
}

/**
 * Standardized radio group with React Hook Form integration
 * Follows enterprise validation display rules
 */
export function FormRadioGroup<T extends FieldValues>({
  name,
  control,
  label,
  options,
  required = false,
  helperText,
  row = false
}: FormRadioGroupProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <FormControl error={shouldShowError(fieldState)} component="fieldset">
          <FormLabel component="legend">
            {label}
            {required && <span style={{ color: 'red' }}> *</span>}
          </FormLabel>
          <RadioGroup
            {...field}
            row={row}
            onChange={(e) => {
              // Convert string values to appropriate types
              const value = e.target.value;
              // Attempt to match the type from options
              const option = options.find(opt => String(opt.value) === value);
              field.onChange(option?.value ?? value);
            }}
            value={String(field.value ?? '')}
          >
            {options.map((option) => {
              const labelProps: any = {
                key: String(option.value),
                value: String(option.value),
                control: <Radio />,
                label: option.label
              };
              
              if (option.disabled !== undefined) {
                labelProps.disabled = option.disabled;
              }
              
              return <FormControlLabel {...labelProps} />;
            })}
          </RadioGroup>
          <FormHelperText>
            {getHelperText(fieldState, helperText)}
          </FormHelperText>
        </FormControl>
      )}
    />
  );
}

export default FormRadioGroup;

