# Overlay Components

Enterprise-grade overlay primitives that decouple behavior from presentation, guarantee accessibility, and expose analytics/i18n hooks.

## Overview

This directory contains two specialized overlay components:

1. **ConfirmDialog** - For simple yes/no confirmations (especially destructive actions)
2. **FormModal** - For form submissions with validation and unsaved changes protection

## Design Philosophy

### Accessibility First
- **Focus Management**: Automatic focus trap, initial focus on open, return focus on close
- **ARIA Attributes**: Proper roles, labels, and descriptions
- **Keyboard Navigation**: Full keyboard support (Escape, Tab, Enter)

### Telemetry & Analytics
- Event hooks for all user interactions (`onOpen`, `onClose`, `onAction`, `onError`)
- Structured event payloads with timestamps and metadata
- Integration-ready for analytics platforms

### Internationalization
- All text accepts `string | ReactNode` for i18n support
- Locale-aware formatting support (when i18n context is available)

### Theming
- Full theme integration (colors, spacing, typography)
- Dark mode support
- Consistent design tokens

## Components

### ConfirmDialog

Simple confirmation dialogs for destructive or important actions.

#### Basic Usage

```tsx
import { ConfirmDialog } from '@/shared/ui/overlays';

function DeleteButton() {
  const [isOpen, setIsOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await deleteItem();
      setIsOpen(false);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Delete</Button>
      
      <ConfirmDialog
        open={isOpen}
        title="Delete Item"
        description="This action cannot be undone."
        confirmAction={{
          label: "Delete",
          variant: "error",
          onClick: handleDelete,
          loading: isDeleting,
        }}
        cancelAction={{
          label: "Cancel",
          variant: "outlined",
          onClick: () => setIsOpen(false),
        }}
      />
    </>
  );
}
```

#### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `open` | `boolean` | Yes | Whether the dialog is open |
| `title` | `string \| ReactNode` | Yes | Dialog title |
| `description` | `string \| ReactNode` | No | Optional description text |
| `confirmAction` | `ActionDescriptor` | Yes | Primary confirm action |
| `cancelAction` | `ActionDescriptor` | No | Cancel action (hidden if not provided) |
| `tertiaryAction` | `ActionDescriptor` | No | Optional tertiary action |
| `error` | `string \| ReactNode \| Error` | No | Error to display in dialog |
| `onOpen` | `(event: OverlayEvent) => void` | No | Callback when dialog opens |
| `onClose` | `(event: OverlayEvent) => void` | No | Callback when dialog closes |
| `onAction` | `(event: OverlayEvent) => void` | No | Callback when action is triggered |
| `overlayId` | `string` | No | Unique identifier (auto-generated if not provided) |
| `maxWidth` | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'` | No | Maximum width (default: `'sm'`) |
| `fullWidth` | `boolean` | No | Whether dialog is full width (default: `true`) |
| `children` | `ReactNode` | No | Custom content (overrides description) |
| `footer` | `ReactNode` | No | Custom footer (overrides default actions) |
| `disableBackdropClick` | `boolean` | No | Disable backdrop click to close |
| `disableEscapeKeyDown` | `boolean` | No | Disable escape key to close |

#### ActionDescriptor

```typescript
interface ActionDescriptor {
  label: string;                    // Button label
  variant: 'error' | 'primary' | 'secondary' | 'outlined';
  onClick: () => void | Promise<void>;  // Handler (sync or async)
  loading?: boolean;                // Loading state
  disabled?: boolean;              // Disabled state
  icon?: ReactNode;                // Optional icon
  testId?: string;                 // Test ID for testing
}
```

#### Examples

**Destructive Action**:
```tsx
<ConfirmDialog
  open={isOpen}
  title="Delete Fund"
  description="Are you sure you want to delete this fund? This action cannot be undone."
  confirmAction={{
    label: "Delete",
    variant: "error",
    onClick: handleDelete,
    loading: isDeleting,
  }}
  cancelAction={{
    label: "Cancel",
    variant: "outlined",
    onClick: () => setIsOpen(false),
  }}
/>
```

**With Analytics**:
```tsx
<ConfirmDialog
  open={isOpen}
  title="Confirm Action"
  confirmAction={confirmAction}
  onOpen={(event) => analytics.track('dialog_opened', event)}
  onClose={(event) => analytics.track('dialog_closed', event)}
  onAction={(event) => analytics.track('dialog_action', event)}
/>
```

**With Error Display**:
```tsx
<ConfirmDialog
  open={isOpen}
  title="Delete Item"
  confirmAction={confirmAction}
  error={deleteError?.message}
/>
```

### FormModal

Form submission modals with React Hook Form integration and dirty-state guard.

#### Basic Usage

```tsx
import { FormModal } from '@/shared/ui/overlays';
import { useForm } from '@/shared/hooks/forms';

function CreateFundModal({ open, onClose }) {
  const form = useForm<FundFormData>({
    schema: fundSchema,
    defaultValues: { name: '', amount: 0 },
    onSubmit: async (data) => {
      await createFund(data);
      onClose();
    },
  });

  return (
    <FormModal
      open={open}
      title="Create Fund"
      subtitle="Enter fund details below"
      onClose={onClose}
      onSubmit={form.handleSubmit}
      isSubmitting={form.formState.isSubmitting}
      isValid={form.formState.isValid}
      isDirty={form.formState.isDirty}
      form={form}
    >
      <FormTextField name="name" control={form.control} />
      <FormNumberField name="amount" control={form.control} />
    </FormModal>
  );
}
```

#### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `open` | `boolean` | Yes | Whether the modal is open |
| `title` | `string \| ReactNode` | Yes | Modal title |
| `subtitle` | `string \| ReactNode` | No | Optional subtitle |
| `onClose` | `() => void` | Yes | Function to call when modal should close |
| `onSubmit` | `() => void \| Promise<void>` | Yes | Function to call when form is submitted |
| `isSubmitting` | `boolean` | No | Whether form is submitting (default: `false`) |
| `isValid` | `boolean` | No | Whether form is valid (default: `true`) |
| `isDirty` | `boolean` | No | Whether form has unsaved changes (default: `false`) |
| `children` | `ReactNode` | Yes | Form content |
| `actions` | `ReactNode` | No | Custom action buttons (overrides default) |
| `showCloseConfirmation` | `boolean` | No | Show confirmation for unsaved changes (default: `true`) |
| `closeConfirmationMessage` | `string` | No | Custom confirmation message |
| `maxWidth` | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'` | No | Modal size (default: `'md'`) |
| `fullWidth` | `boolean` | No | Whether modal is full width (default: `true`) |
| `error` | `string \| ReactNode \| Error` | No | Error to display in modal |
| `form` | `UseFormReturn<FieldValues>` | No | React Hook Form instance (can use `useFormContext` instead) |
| `onOpen` | `(event: OverlayEvent) => void` | No | Callback when modal opens |
| `onCloseEvent` | `(event: OverlayEvent) => void` | No | Callback when modal closes |
| `onSubmitEvent` | `(event: OverlayEvent) => void` | No | Callback when form is submitted |
| `onError` | `(event: OverlayEvent & { error: Error \| string }) => void` | No | Callback when error occurs |
| `overlayId` | `string` | No | Unique identifier (auto-generated if not provided) |
| `disableBackdropClick` | `boolean` | No | Disable backdrop click to close |
| `disableEscapeKeyDown` | `boolean` | No | Disable escape key to close |

#### React Hook Form Integration

FormModal can work with React Hook Form in two ways:

**1. Explicit Form Instance**:
```tsx
const form = useForm({ ... });
<FormModal form={form} ... />
```

**2. Form Context** (recommended):
```tsx
<FormProvider {...form}>
  <FormModal ... />  {/* Automatically uses form from context */}
</FormProvider>
```

#### Dirty State Guard

When `isDirty={true}` and `showCloseConfirmation={true}`, the modal will show a confirmation dialog before closing:

```tsx
<FormModal
  isDirty={form.formState.isDirty}
  showCloseConfirmation={true}
  closeConfirmationMessage="You have unsaved changes. Are you sure?"
  // ...
/>
```

#### Examples

**Basic Form**:
```tsx
<FormModal
  open={isOpen}
  title="Create Fund"
  onClose={() => setIsOpen(false)}
  onSubmit={form.handleSubmit(onSubmit)}
  isSubmitting={isPending}
  isValid={form.formState.isValid}
  isDirty={form.formState.isDirty}
>
  <FormTextField name="name" control={form.control} />
</FormModal>
```

**With Error Handling**:
```tsx
<FormModal
  open={isOpen}
  title="Create Fund"
  onSubmit={form.handleSubmit(onSubmit)}
  error={submitError?.message}
  onError={(event) => {
    errorLogger.logError(event.error);
    analytics.track('form_error', event);
  }}
>
  {/* form fields */}
</FormModal>
```

## Accessibility Guarantees

Both components guarantee:

- ✅ **Focus Management**: Focus trapped within overlay, returns to trigger on close
- ✅ **ARIA Attributes**: Proper roles, labels, and descriptions
- ✅ **Keyboard Navigation**: Full keyboard support (Escape, Tab, Enter, Shift+Tab)
- ✅ **Screen Reader Support**: All content properly announced
- ✅ **Loading States**: Disabled states and loading indicators properly announced

## Telemetry Events

### OverlayEvent Structure

```typescript
interface OverlayEvent {
  overlayId: string;              // Unique identifier
  overlayType: 'confirm' | 'form'; // Type of overlay
  action?: string;                 // Action taken
  timestamp: Date;                  // Event timestamp
  metadata?: Record<string, unknown>; // Additional context
}
```

### Event Types

**ConfirmDialog**:
- `onOpen`: Fired when dialog opens (`action: 'open'`)
- `onClose`: Fired when dialog closes (`action: 'backdrop' | 'escape' | 'cancel'`)
- `onAction`: Fired when action button clicked (`action: 'confirm' | 'cancel' | 'tertiary'`)

**FormModal**:
- `onOpen`: Fired when modal opens (`action: 'open'`)
- `onCloseEvent`: Fired when modal closes (`action: 'backdrop' | 'escape' | 'cancel'`)
- `onSubmitEvent`: Fired when form is submitted (`action: 'submit'`)
- `onError`: Fired when error occurs (`action: 'error'`, includes `error` field)

### Analytics Integration Example

```tsx
<ConfirmDialog
  open={isOpen}
  title="Delete Item"
  confirmAction={confirmAction}
  onOpen={(event) => {
    analytics.track('dialog_opened', {
      dialog_type: event.overlayType,
      dialog_id: event.overlayId,
    });
  }}
  onAction={(event) => {
    analytics.track('dialog_action', {
      dialog_type: event.overlayType,
      action: event.action,
      timestamp: event.timestamp,
    });
  }}
/>
```

## Migration Checklist

When migrating from legacy components:

- [ ] Update imports: `@/shared/ui/overlays` instead of `@/components/shared/overlays`
- [ ] Convert props to new API:
  - `ConfirmDialog`: Convert to `ConfirmDialog` with `confirmAction` and `cancelAction`
  - `FormModal`: Convert to `FormModal` (API is similar, but check prop names)
- [ ] Add analytics callbacks if needed
- [ ] Test focus management and keyboard navigation
- [ ] Verify dirty state guard behavior (FormModal)
- [ ] Update tests to use new component APIs

## Testing

Both components have comprehensive test coverage:

- ✅ Rendering (open/closed states)
- ✅ User interactions (button clicks, keyboard)
- ✅ Loading and error states
- ✅ Analytics callbacks
- ✅ Accessibility (ARIA attributes)
- ✅ Dirty state guard (FormModal)

See component-specific test files:
- `ConfirmDialog/ConfirmDialog.test.tsx`
- `FormModal/FormModal.test.tsx`

## Related Components

- **Forms**: `FormTextField`, `FormNumberField` (work with FormModal)
- **Feedback**: `ErrorDisplay`, `LoadingSpinner` (can be used inside modals)
- **Hooks**: `useForm` from `@/shared/hooks/forms` (for FormModal)
