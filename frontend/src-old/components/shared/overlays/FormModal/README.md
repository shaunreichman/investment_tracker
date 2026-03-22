# FormModal

A specialized modal wrapper for forms with built-in submission handling, validation states, and unsaved changes protection. Designed to work seamlessly with React Hook Form.

## Purpose

Use `FormModal` when you need to:
- Display a form in a modal overlay
- Handle form submission with loading states
- Protect against accidental closure with unsaved changes
- Integrate with React Hook Form validation
- Show multi-step forms or complex data entry

## Features

- ✅ **React Hook Form Integration**: Works seamlessly with RHF's `isValid`, `isDirty`, `isSubmitting`
- ✅ **Unsaved Changes Protection**: Warns before closing with unsaved data
- ✅ **Flexible Sizing**: Configurable modal width (xs, sm, md, lg, xl)
- ✅ **Loading States**: Disables inputs and shows progress during submission
- ✅ **Custom Actions**: Override default buttons for specialized workflows
- ✅ **Accessible**: Full keyboard navigation and screen reader support

## Usage

### Basic Form with React Hook Form

```tsx
import { FormModal } from '@/components/shared/overlays';
import { useForm } from 'react-hook-form';
import { FormTextField, FormNumberField } from '@/components/shared/forms';

interface FundFormData {
  name: string;
  amount: number;
}

function CreateFundModal({ open, onClose }) {
  const { control, handleSubmit, formState } = useForm<FundFormData>();
  const { mutate, isPending } = useCreateFund();

  const onSubmit = (data: FundFormData) => {
    mutate(data, {
      onSuccess: () => onClose()
    });
  };

  return (
    <FormModal
      open={open}
      title="Create New Fund"
      subtitle="Enter fund details below"
      onClose={onClose}
      onSubmit={handleSubmit(onSubmit)}
      isSubmitting={isPending}
      isValid={formState.isValid}
      isDirty={formState.isDirty}
      maxWidth="md"
    >
      <FormTextField
        name="name"
        label="Fund Name"
        control={control}
        rules={{ required: 'Fund name is required' }}
      />
      
      <FormNumberField
        name="amount"
        label="Initial Amount"
        control={control}
        rules={{ required: 'Amount is required', min: 0 }}
      />
    </FormModal>
  );
}
```

### With Custom Actions

```tsx
<FormModal
  open={open}
  title="Review Changes"
  onClose={onClose}
  onSubmit={handleSubmit}
  actions={
    <>
      <Button onClick={onClose} variant="outlined">
        Cancel
      </Button>
      <Button onClick={handleSaveDraft} variant="outlined">
        Save Draft
      </Button>
      <Button onClick={handleSubmit} variant="contained">
        Publish
      </Button>
    </>
  }
>
  {/* Form content */}
</FormModal>
```

### Without Unsaved Changes Warning

```tsx
<FormModal
  open={open}
  title="Quick Filter"
  onClose={onClose}
  onSubmit={handleApplyFilter}
  showCloseConfirmation={false}
>
  {/* Filter form - no need to warn on close */}
</FormModal>
```

### Large Form

```tsx
<FormModal
  open={open}
  title="Create Event"
  subtitle="Select event type and enter details"
  onClose={onClose}
  onSubmit={handleSubmit(onSubmit)}
  isSubmitting={isPending}
  isValid={formState.isValid}
  isDirty={formState.isDirty}
  maxWidth="lg"
  fullWidth
>
  {/* Multi-step form or complex layout */}
</FormModal>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `open` | `boolean` | **required** | Whether the modal is open |
| `title` | `string` | **required** | Modal title |
| `subtitle` | `string` | `undefined` | Optional subtitle text |
| `onClose` | `() => void` | **required** | Called when modal should close |
| `onSubmit` | `() => void` | **required** | Called when form is submitted |
| `isSubmitting` | `boolean` | `false` | Form submission in progress |
| `isValid` | `boolean` | `true` | Whether form is valid (enables submit) |
| `isDirty` | `boolean` | `false` | Whether form has unsaved changes |
| `children` | `ReactNode` | **required** | Form content |
| `actions` | `ReactNode` | `undefined` | Custom action buttons |
| `showCloseConfirmation` | `boolean` | `true` | Show warning on close with unsaved changes |
| `maxWidth` | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Maximum width of modal |
| `fullWidth` | `boolean` | `true` | Whether modal takes full available width |

## Integration with React Hook Form

`FormModal` is designed to work seamlessly with React Hook Form's `formState`:

```tsx
const { control, handleSubmit, formState } = useForm<MyFormData>({
  mode: 'onChange', // Validate on change for real-time isValid
});

<FormModal
  onSubmit={handleSubmit(onSubmit)} // RHF's handleSubmit wrapper
  isSubmitting={formState.isSubmitting} // RHF's submission state
  isValid={formState.isValid} // RHF's validation state
  isDirty={formState.isDirty} // RHF's dirty tracking
>
```

## Accessibility

- **ARIA**: Dialog properly labeled with title
- **Keyboard Navigation**:
  - `Escape` closes modal (with confirmation if dirty)
  - `Tab` cycles through form fields and buttons
  - `Enter` submits form (when submit button is focused)
- **Focus Management**: Focus trapped within modal when open
- **Screen Readers**: Loading states and disabled states properly announced

## Best Practices

### When to Use

✅ **Use FormModal when:**
- Creating or editing resources (funds, entities, events)
- Multi-field data entry
- Forms that need validation before submission
- Operations that require user input

❌ **Don't use FormModal for:**
- Simple confirmations (use `ConfirmDialog` instead)
- Read-only information (use standard Modal or Dialog)
- Single-field input (consider inline editing)

### UX Guidelines

1. **Clear Titles**: Describe what the form does ("Create Fund", "Edit Entity")
2. **Helpful Subtitles**: Provide context when needed
3. **Proper Sizing**: 
   - `sm` for 2-3 fields
   - `md` for 4-8 fields
   - `lg` for complex forms or multi-step flows
4. **Validation**: Always connect to RHF's `isValid` to prevent invalid submissions
5. **Loading States**: Always show loading during async operations
6. **Unsaved Protection**: Keep `showCloseConfirmation={true}` for data entry forms

## Size Guidelines

| Size | Max Width | Use Case |
|------|-----------|----------|
| `xs` | 444px | Very simple forms (1-2 fields) |
| `sm` | 600px | Basic forms (3-4 fields) |
| `md` | 900px | Standard forms (5-8 fields) |
| `lg` | 1200px | Complex forms, multi-step wizards |
| `xl` | 1536px | Full-featured editors |

## Examples from Codebase

### Create Fund Modal

```tsx
<FormModal
  open={createModalOpen}
  title="Create New Fund"
  subtitle={`Creating fund for ${companyName}`}
  onClose={() => setCreateModalOpen(false)}
  onSubmit={handleSubmit(onSubmit)}
  isSubmitting={createFundMutation.isPending}
  isValid={formState.isValid}
  isDirty={formState.isDirty}
  maxWidth="lg"
>
  <TemplateSelector templates={templates} onSelect={applyTemplate} />
  <FormTextField name="name" label="Fund Name" control={control} />
  {/* More form fields... */}
</FormModal>
```

## Related Components

- **ConfirmDialog**: For simple yes/no confirmations
- **Form Components**: `FormTextField`, `FormNumberField`, `FormDateField`
- **React Hook Form**: Core form state management

## Migration Notes

This component replaces `components/ui/FormContainer.tsx`. Key changes:
- Renamed from `FormContainer` to `FormModal` for clarity
- Enhanced TypeScript types
- Improved documentation
- Better theme integration
- Same API, fully backward compatible

