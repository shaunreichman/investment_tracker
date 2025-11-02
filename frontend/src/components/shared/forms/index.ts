/**
 * Forms Components Barrel Export
 * 
 * Reusable form field components for React Hook Form + Zod integration.
 * All components follow enterprise validation display rules.
 * 
 * @example
 * ```typescript
 * import { FormTextField, FormNumberField, FormDateField } from '@/components/shared/forms';
 * ```
 */

// Text Input Components
export { FormTextField } from './FormTextField';
export { FormTextArea } from './FormTextArea';
export { FormNumberField } from './FormNumberField';
export { FormDateField } from './FormDateField';

// Selection Components
export { FormSelectField } from './FormSelectField';
export { FormRadioGroup } from './FormRadioGroup';

// Boolean Input Components
export { FormCheckbox } from './FormCheckbox';
export { FormSwitch } from './FormSwitch';

// Primitives (low-level form-agnostic components)
export { NumberInputField } from './primitives';
export type { NumberInputFieldProps } from './primitives';

// Utilities
export { 
  shouldShowError, 
  getFieldLabel, 
  getHelperText, 
  getFieldColor,
  useFieldState 
} from './utils';

// Types
export type { SelectOption, RadioOption } from './types';
