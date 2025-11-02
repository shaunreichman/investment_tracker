# Shared Form Components

Enterprise-grade form components for React Hook Form + Zod validation integration.

## Overview

This directory contains reusable form field components that provide:
- **Consistent API** across all field types
- **React Hook Form integration** via Controller pattern
- **Enterprise validation UX** (blue borders for required, red for errors, asterisks for required)
- **Zero code duplication** via shared utility functions
- **Type-safe** with TypeScript generics
- **Accessible** with proper ARIA attributes and semantic HTML

## Architecture

### Design Principles
- **DRY (Don't Repeat Yourself)**: All validation display logic centralized in `utils.ts`
- **Single Source of Truth**: One place to update UX behavior across all components
- **Visual Hierarchy**: Clear color-coded states (blue = required, red = error, gray = normal)
- **Progressive Disclosure**: Errors shown only after user interaction
- **Consistent Behavior**: All components use the same utility functions

### Two-Layer Architecture

```
primitives/              → Form-library-agnostic controlled inputs
├── NumberInputField     → Number formatting, focus/blur behavior
└── (future primitives)  → Date pickers, rich text editors, etc.
         ↓ (wrapped by)
Form*Field components    → React Hook Form integration layer
├── FormTextField        → RHF + validation display
├── FormNumberField      → RHF wrapper around NumberInputField
└── FormDateField        → RHF + validation display
```

**Primitives Directory**:
- Contains low-level, reusable input components
- Form-library-agnostic (can be used with manual state, Formik, etc.)
- Provides specialized behavior (number formatting, date handling, etc.)
- No React Hook Form dependencies

**Form*Field Components**:
- Wrap primitives or Material-UI components
- Integrate with React Hook Form via Controller
- Apply consistent validation display rules
- Handle error messages, helper text, and visual states

## Components

### Text Input Components

#### FormTextField
Single-line text input for general text entry.

```typescript
import { FormTextField } from '@/components/shared/forms';

<FormTextField
  name="username"
  control={control}
  label="Username"
  required
  helperText="Choose a unique username"
/>
```

#### FormTextArea
Multi-line text input for longer text content.

```typescript
import { FormTextArea } from '@/components/shared/forms';

<FormTextArea
  name="description"
  control={control}
  label="Description"
  rows={4}
  placeholder="Enter a detailed description..."
  helperText="Provide context for this item"
/>
```

#### FormNumberField
Number input with thousand separator formatting and decimal support.

```typescript
import { FormNumberField } from '@/components/shared/forms';

<FormNumberField
  name="amount"
  control={control}
  label="Amount"
  required
  allowDecimals
  helperText="Enter the investment amount"
/>
```

#### FormDateField
Date picker using native browser input.

```typescript
import { FormDateField } from '@/components/shared/forms';

<FormDateField
  name="transactionDate"
  control={control}
  label="Transaction Date"
  required
/>
```

### Selection Components

#### FormSelectField
Dropdown select for choosing one option from a list.

```typescript
import { FormSelectField } from '@/components/shared/forms';

<FormSelectField
  name="status"
  control={control}
  label="Status"
  required
  options={[
    { value: 'active', label: 'Active' },
    { value: 'pending', label: 'Pending' },
    { value: 'closed', label: 'Closed' }
  ]}
/>
```

#### FormRadioGroup
Radio buttons for selecting one option with visible choices.

```typescript
import { FormRadioGroup } from '@/components/shared/forms';

<FormRadioGroup
  name="fundType"
  control={control}
  label="Fund Type"
  required
  row
  options={[
    { value: 'equity', label: 'Equity Fund' },
    { value: 'debt', label: 'Debt Fund' },
    { value: 'hybrid', label: 'Hybrid Fund' }
  ]}
/>
```

### Boolean Input Components

#### FormCheckbox
Single checkbox for boolean values.

```typescript
import { FormCheckbox } from '@/components/shared/forms';

<FormCheckbox
  name="acceptTerms"
  control={control}
  label="I accept the terms and conditions"
  required
/>
```

#### FormSwitch
Toggle switch for boolean values with prominent on/off indicator.

```typescript
import { FormSwitch } from '@/components/shared/forms';

<FormSwitch
  name="isActive"
  control={control}
  label="Active Status"
  helperText="Enable or disable this item"
/>
```

## Usage Pattern

### Complete Form Example

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  FormTextField, 
  FormNumberField, 
  FormSelectField,
  FormTextArea,
  FormCheckbox 
} from '@/components/shared/forms';

// 1. Define Zod schema
const fundSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  amount: z.number().min(0, 'Amount must be positive'),
  status: z.enum(['active', 'pending', 'closed']),
  description: z.string().optional(),
  isPublic: z.boolean()
});

type FundFormData = z.infer<typeof fundSchema>;

// 2. Component with form
function CreateFundForm() {
  const { control, handleSubmit } = useForm<FundFormData>({
    resolver: zodResolver(fundSchema),
    defaultValues: {
      name: '',
      amount: 0,
      status: 'pending',
      description: '',
      isPublic: false
    }
  });

  const onSubmit = (data: FundFormData) => {
    console.log('Form data:', data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <FormTextField
        name="name"
        control={control}
        label="Fund Name"
        required
      />
      
      <FormNumberField
        name="amount"
        control={control}
        label="Initial Amount"
        required
        allowDecimals
      />
      
      <FormSelectField
        name="status"
        control={control}
        label="Status"
        required
        options={[
          { value: 'active', label: 'Active' },
          { value: 'pending', label: 'Pending' },
          { value: 'closed', label: 'Closed' }
        ]}
      />
      
      <FormTextArea
        name="description"
        control={control}
        label="Description"
        rows={4}
      />
      
      <FormCheckbox
        name="isPublic"
        control={control}
        label="Make this fund public"
      />
      
      <button type="submit">Create Fund</button>
    </form>
  );
}
```

## Validation Display Rules

All components follow enterprise-grade validation UX with visual priority hierarchy:

### Visual States

```
┌─────────────────────────────────────┐
│ REQUIRED FIELD (Initial Load)      │
│ Fund Name * [BLUE BORDER]          │  ← Blue indicates "you need to fill this"
│ Enter a unique fund name           │  ← Helper text guides user
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ERROR STATE (After Touch)          │
│ Fund Name * [RED BORDER]           │  ← Red indicates "there's a problem"
│ ⚠️ Fund name is required            │  ← Error message explains issue
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ VALID STATE (After Entry)          │
│ Fund Name * [NORMAL BORDER]        │  ← Normal gray indicates "all good"
│ Enter a unique fund name           │  ← Helper text returns
└─────────────────────────────────────┘
```

### Rules

1. **Required Indicator (Always Visible)**
   - Red asterisk (*) always visible for required fields
   - Shows immediately on page load
   - Persists through all states

2. **Blue Border (Initial State for Required)**
   - Required empty fields show blue border (`color="info"`)
   - Provides immediate visual feedback about what needs attention
   - Helps users scan the form to understand requirements
   - Disappears once user enters valid data

3. **Red Border (Error State)**
   - Shown ONLY when field is touched AND has validation error
   - Replaces blue border when error occurs
   - Clear visual signal that immediate action is needed

4. **Error Display (Progressive Disclosure)**
   - Errors shown ONLY after user has interacted with field (`isTouched`)
   - Prevents overwhelming users with errors on page load
   - Better UX than showing all errors immediately

5. **Helper Text vs Error Messages**
   - Error messages override helper text when error is present
   - Helper text returns when error is cleared
   - Provides context guidance when no errors exist

## Component API

### Common Props (All Components)

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `name` | `Path<T>` | ✓ | Field name from form schema |
| `control` | `Control<T>` | ✓ | React Hook Form control instance |
| `label` | `string` | ✓ | Display label for the field |
| `required` | `boolean` |  | Whether field is required (shows red asterisk) |
| `helperText` | `string` |  | Helper text shown when no error |

### Field-Specific Props

#### FormTextField / FormTextArea
- `placeholder?: string` - Placeholder text
- `textFieldProps?: TextFieldProps` - Additional Material-UI props

#### FormNumberField
- `allowDecimals?: boolean` - Allow decimal values (default: true)
- `allowNegative?: boolean` - Allow negative values (default: false)

#### FormSelectField / FormRadioGroup
- `options: SelectOption[]` - Array of { value, label } options

#### FormCheckbox / FormSwitch
- `disabled?: boolean` - Disable the input

## Types

### SelectOption
```typescript
interface SelectOption {
  value: string | number;
  label: string;
}
```

### RadioOption
```typescript
interface RadioOption {
  value: string | number | boolean;
  label: string;
  disabled?: boolean;
}
```

## Utility Functions

All form components use centralized utility functions from `utils.ts` to ensure consistency and eliminate code duplication.

### shouldShowError

Determines if a field error should be displayed.

```typescript
import { shouldShowError } from '@/components/shared/forms';

const showError = shouldShowError(fieldState);
// Returns: true if field has error AND user has touched it
```

**Enterprise UX Rule**: Only show errors AFTER user interaction to prevent hostile UX.

### getFieldLabel

Generates a label with optional required indicator.

```typescript
import { getFieldLabel } from '@/components/shared/forms';

const label = getFieldLabel('Fund Name', true);
// Returns: <span>Fund Name <span style={{ color: 'red' }}> *</span></span>
```

### getFieldColor

Gets the appropriate border color based on validation state.

```typescript
import { getFieldColor } from '@/components/shared/forms';

const color = getFieldColor(fieldState, required);
// Returns: 'error' | 'info' | 'primary'
```

**Color Priority**:
1. **Red** (`error`): Field touched + has error → immediate attention needed
2. **Blue** (`info`): Required + empty → user should complete this
3. **Gray** (`primary`): Normal state → no special attention needed

### getHelperText

Gets appropriate helper text based on validation state.

```typescript
import { getHelperText } from '@/components/shared/forms';

const helperText = getHelperText(fieldState, 'Enter your name');
// Returns: error message if error present, otherwise helper text
```

### useFieldState

Convenience hook that bundles all utilities together.

```typescript
import { useFieldState } from '@/components/shared/forms';

const { showError, fieldColor, displayLabel, displayHelperText } = useFieldState(
  fieldState,
  'Fund Name',
  true,  // required
  'Enter a unique name'
);

<TextField
  label={displayLabel}
  color={fieldColor}
  error={showError}
  helperText={displayHelperText}
/>
```

### Why These Utilities Matter

**Before** (Code duplication in every component):
```typescript
// Repeated in every form component ❌
const showError = !!fieldState.error && fieldState.isTouched;
const label = (
  <span>
    {label}
    {required && <span style={{ color: 'red' }}> *</span>}
  </span>
);
```

**After** (Single source of truth):
```typescript
// Centralized utility ✅
import { shouldShowError, getFieldLabel } from './utils';

<TextField
  label={getFieldLabel(label, required)}
  error={shouldShowError(fieldState)}
/>
```

**Benefits**:
- ✅ Update validation UX in one place, affects all components
- ✅ Consistent behavior across entire form system
- ✅ Self-documenting (function names explain intent)
- ✅ Easier to test
- ✅ Easier to extend with new features

## Best Practices

1. **Use with Zod schemas** - Define validation in Zod schemas for type inference
2. **Provide meaningful labels** - Clear, concise labels improve UX
3. **Add helper text** - Guide users with helpful context
4. **Group related fields** - Use logical sections in forms
5. **Test keyboard navigation** - Ensure all fields are accessible via keyboard

## Migration from Manual State

**Before** (Manual state management):
```typescript
const [formData, setFormData] = useState({ name: '' });
const [errors, setErrors] = useState({});

<input
  value={formData.name}
  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
/>
```

**After** (React Hook Form + shared components):
```typescript
const { control } = useForm<FormData>({
  resolver: zodResolver(schema)
});

<FormTextField name="name" control={control} label="Name" />
```

## Adding New Components

When adding new form components:

1. **Use utility functions** - Import from `./utils` for validation display logic
   ```typescript
   import { shouldShowError, getFieldLabel, getHelperText, getFieldColor } from './utils';
   ```

2. **Follow existing patterns** - Use Controller, consistent prop naming

3. **Implement validation UX** - Apply utilities in render:
   ```typescript
   <Controller
     name={name}
     control={control}
     render={({ field, fieldState }) => (
       <TextField
         {...field}
         label={getFieldLabel(label, required)}
         color={getFieldColor(fieldState, required)}
         error={shouldShowError(fieldState)}
         helperText={getHelperText(fieldState, helperText)}
       />
     )}
   />
   ```

4. **Add TypeScript types** - Use generics for type safety

5. **Document thoroughly** - JSDoc comments and examples

6. **Export from index.ts** - Add to barrel export

7. **Update this README** - Document usage and API

### Example: Creating a New Form Component

```typescript
import React from 'react';
import { TextField } from '@mui/material';
import { Controller, Control, FieldValues, Path } from 'react-hook-form';
import { shouldShowError, getFieldLabel, getHelperText, getFieldColor } from './utils';

interface FormCustomFieldProps<T extends FieldValues> {
  name: Path<T>;
  control: Control<T>;
  label: string;
  required?: boolean;
  helperText?: string;
}

export function FormCustomField<T extends FieldValues>({
  name,
  control,
  label,
  required = false,
  helperText
}: FormCustomFieldProps<T>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <TextField
          {...field}
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
```

**Key Points**:
- ✅ All validation logic comes from utilities
- ✅ No duplicated code
- ✅ Consistent with other form components
- ✅ Easy to maintain and extend

