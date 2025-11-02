# Shared Overlay Components

Reusable modal and dialog components for consistent overlay UX across the application.

## Overview

This directory contains two specialized overlay patterns:

1. **ConfirmDialog** - For simple yes/no confirmations (especially destructive actions)
2. **FormModal** - For form submissions with validation and unsaved changes protection

## When to Use Which

### Use ConfirmDialog for:
- ✅ Delete confirmations
- ✅ Irreversible operations
- ✅ Simple yes/no decisions
- ✅ Quick user consent

**Example**: "Delete Fund?", "Remove Entity?", "Discard Changes?"

### Use FormModal for:
- ✅ Creating/editing resources
- ✅ Multi-field data entry
- ✅ Forms with validation
- ✅ Complex input workflows

**Example**: "Create Fund", "Edit Entity", "Add Event"

### Use MUI Dialog directly for:
- 📋 Read-only information displays
- 📋 Custom workflows not covered by the above patterns
- 📋 Highly specialized use cases

## Quick Start

### ConfirmDialog Example

```tsx
import { ConfirmDialog } from '@/components/shared/overlays';

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Delete</Button>
      
      <ConfirmDialog
        open={isOpen}
        title="Delete Fund"
        description="This action cannot be undone."
        onConfirm={handleDelete}
        onCancel={() => setIsOpen(false)}
        confirmVariant="error"
      />
    </>
  );
}
```

### FormModal Example

```tsx
import { FormModal } from '@/components/shared/overlays';
import { useForm } from 'react-hook-form';

function CreateFundModal({ open, onClose }) {
  const { control, handleSubmit, formState } = useForm();

  return (
    <FormModal
      open={open}
      title="Create Fund"
      onClose={onClose}
      onSubmit={handleSubmit(onSubmit)}
      isSubmitting={isPending}
      isValid={formState.isValid}
      isDirty={formState.isDirty}
    >
      <FormTextField name="name" control={control} />
    </FormModal>
  );
}
```

## Component Documentation

Each component has detailed documentation in its respective directory:

- [ConfirmDialog/README.md](./ConfirmDialog/README.md) - Full API, examples, and best practices
- [FormModal/README.md](./FormModal/README.md) - RHF integration, sizing, and guidelines

## Design Principles

### 1. Specialized Over Generic
We provide two specialized patterns rather than a single generic "Modal" component. This makes it clear which component to use for which scenario and provides better type safety and UX out of the box.

### 2. Accessibility First
All overlay components include:
- Proper ARIA labels and roles
- Keyboard navigation (Escape, Tab, Enter)
- Focus management
- Screen reader support

### 3. Theme Integration
Components use the application's theme system for consistent styling:
- Dark mode support
- Consistent spacing, borders, shadows
- Theme-aware colors

### 4. Loading States
Both components handle loading states properly:
- Disabled buttons during operations
- Loading indicators
- Clear visual feedback

## Common Patterns

### 1. Delete Confirmation Flow

```tsx
const [deleteDialog, setDeleteDialog] = useState<{ 
  open: boolean; 
  item: Item | null 
}>({ open: false, item: null });

const { mutate: deleteItem, isPending } = useDeleteItem();

const handleDeleteClick = (item: Item) => {
  setDeleteDialog({ open: true, item });
};

const handleConfirmDelete = () => {
  if (!deleteDialog.item) return;
  deleteItem(deleteDialog.item.id, {
    onSuccess: () => setDeleteDialog({ open: false, item: null })
  });
};

return (
  <>
    <Button onClick={() => handleDeleteClick(item)}>Delete</Button>
    
    <ConfirmDialog
      open={deleteDialog.open}
      title={`Delete ${deleteDialog.item?.name}`}
      description="This action cannot be undone."
      onConfirm={handleConfirmDelete}
      onCancel={() => setDeleteDialog({ open: false, item: null })}
      loading={isPending}
      confirmVariant="error"
    />
  </>
);
```

### 2. Create/Edit Form Flow

```tsx
const [modalOpen, setModalOpen] = useState(false);
const { control, handleSubmit, formState, reset } = useForm<FormData>();
const { mutate, isPending } = useCreateItem();

const onSubmit = (data: FormData) => {
  mutate(data, {
    onSuccess: () => {
      setModalOpen(false);
      reset();
    }
  });
};

return (
  <>
    <Button onClick={() => setModalOpen(true)}>Create</Button>
    
    <FormModal
      open={modalOpen}
      title="Create Item"
      onClose={() => setModalOpen(false)}
      onSubmit={handleSubmit(onSubmit)}
      isSubmitting={isPending}
      isValid={formState.isValid}
      isDirty={formState.isDirty}
    >
      <FormTextField name="name" label="Name" control={control} />
    </FormModal>
  </>
);
```

## Styling Guidelines

### Modal Sizes

Choose the appropriate size for your form:

| Size | Max Width | Use Case |
|------|-----------|----------|
| `xs` | 444px | 1-2 fields |
| `sm` | 600px | 3-4 fields |
| `md` | 900px | 5-8 fields (default) |
| `lg` | 1200px | Complex forms, multi-step |
| `xl` | 1536px | Full editors |

### Button Variants

**ConfirmDialog** supports three variants:
- `error` - Red, for destructive actions (default)
- `primary` - Blue, for important non-destructive actions
- `secondary` - Gray, for neutral confirmations

## Migration Guide

### From `components/ui/ConfirmDialog.tsx`

The API is unchanged - simply update imports:

```tsx
// Before
import { ConfirmDialog } from '@/components/ui';

// After
import { ConfirmDialog } from '@/components/shared/overlays';
```

### From `components/ui/FormContainer.tsx`

Component renamed to `FormModal`, but API is the same:

```tsx
// Before
import { FormContainer } from '@/components/ui';

<FormContainer
  open={open}
  title="Create Fund"
  onClose={onClose}
  onSubmit={onSubmit}
  isSubmitting={isPending}
  isValid={isValid}
  isDirty={isDirty}
>
  {/* form content */}
</FormContainer>

// After
import { FormModal } from '@/components/shared/overlays';

<FormModal
  open={open}
  title="Create Fund"
  onClose={onClose}
  onSubmit={onSubmit}
  isSubmitting={isPending}
  isValid={isValid}
  isDirty={isDirty}
>
  {/* form content */}
</FormModal>
```

## Architecture Notes

### Why No Generic "Modal" Component?

We intentionally don't provide a generic `Modal` wrapper component for these reasons:

1. **Clear Patterns**: Two specialized components make it obvious which to use
2. **Type Safety**: Each component has props specific to its use case
3. **No Unnecessary Abstraction**: Developers can use MUI `Dialog` directly for custom cases
4. **Avoid Over-Engineering**: We follow "Rule of Three" - only abstract when pattern repeats 3+ times

### When to Create a New Overlay Component

Consider creating a new specialized overlay component when:
- The pattern is used in 3+ places across the codebase
- It has distinct behavior not covered by ConfirmDialog or FormModal
- It provides genuine value over using MUI Dialog directly

**Example**: If we frequently show error dialogs with dependency lists (like `DependencyBlockedDialog`), that could justify a specialized component.

## Related Components

- **Forms**: `FormTextField`, `FormNumberField`, `FormDateField` (work with FormModal)
- **Feedback**: `LoadingSpinner`, `ErrorDisplay` (can be used inside modals)
- **Navigation**: `Breadcrumbs`, `Tabs` (navigate to modals or within them)

## Testing

Both components should be tested for:
- Opening and closing behavior
- Keyboard navigation (Escape, Tab, Enter)
- Loading states
- Unsaved changes warning (FormModal)
- Accessibility (ARIA labels, focus management)

See individual component README files for specific test examples.

