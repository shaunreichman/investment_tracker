# ConfirmDialog

A reusable confirmation dialog component for destructive or important actions that require explicit user consent.

## Purpose

Use `ConfirmDialog` when you need to:
- Confirm destructive actions (delete, remove, etc.)
- Get explicit user consent for irreversible operations
- Display a simple yes/no decision to the user
- Show a warning before proceeding with an action

## Features

- ✅ **Accessible**: Full ARIA support with proper labeling
- ✅ **Loading States**: Built-in support for async operations
- ✅ **Variants**: Error, primary, and secondary button styles
- ✅ **Keyboard Navigation**: Escape key closes, Enter key confirms
- ✅ **Theme Integration**: Respects application theme

## Usage

### Basic Delete Confirmation

```tsx
import { ConfirmDialog } from '@/components/shared/overlays';

function MyComponent() {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const handleDelete = () => {
    // Perform delete operation
    setDeleteDialogOpen(false);
  };

  return (
    <>
      <Button onClick={() => setDeleteDialogOpen(true)}>Delete Fund</Button>
      
      <ConfirmDialog
        open={deleteDialogOpen}
        title="Delete Fund"
        description="Are you sure you want to delete this fund? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        onConfirm={handleDelete}
        onCancel={() => setDeleteDialogOpen(false)}
        confirmVariant="error"
      />
    </>
  );
}
```

### With Async Operation

```tsx
function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);
  const { mutate: deleteFund, isPending } = useDeleteFund();

  const handleConfirm = () => {
    deleteFund(fundId, {
      onSuccess: () => setIsOpen(false)
    });
  };

  return (
    <ConfirmDialog
      open={isOpen}
      title="Delete Fund"
      description="This will permanently delete the fund and all associated data."
      onConfirm={handleConfirm}
      onCancel={() => setIsOpen(false)}
      loading={isPending}
      confirmVariant="error"
    />
  );
}
```

### Primary Action (Non-Destructive)

```tsx
<ConfirmDialog
  open={open}
  title="Publish Report"
  description="This will make the report visible to all team members."
  confirmLabel="Publish"
  cancelLabel="Cancel"
  onConfirm={handlePublish}
  onCancel={handleCancel}
  confirmVariant="primary"
/>
```

### No Description (Simple Confirmation)

```tsx
<ConfirmDialog
  open={open}
  title="Are you sure?"
  onConfirm={handleConfirm}
  onCancel={handleCancel}
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `open` | `boolean` | **required** | Whether the dialog is open |
| `title` | `string` | **required** | Dialog title |
| `description` | `string` | `undefined` | Optional description text |
| `confirmLabel` | `string` | `'Confirm'` | Label for confirm button |
| `cancelLabel` | `string` | `'Cancel'` | Label for cancel button |
| `onConfirm` | `() => void` | **required** | Callback when confirm is clicked |
| `onCancel` | `() => void` | `undefined` | Callback when cancel is clicked |
| `loading` | `boolean` | `false` | Shows loading state, disables buttons |
| `disabled` | `boolean` | `false` | Disables the confirm button |
| `confirmVariant` | `'error' \| 'primary' \| 'secondary'` | `'error'` | Visual variant for confirm button |

## Accessibility

- **ARIA Labels**: Dialog properly labeled with `aria-labelledby` and `aria-describedby`
- **Keyboard Navigation**: 
  - `Escape` key closes the dialog (calls `onCancel`)
  - `Enter` key confirms (when focused on confirm button)
  - `Tab` cycles through interactive elements
- **Focus Management**: Focus automatically moves to dialog when opened

## Best Practices

### When to Use

✅ **Use ConfirmDialog when:**
- Deleting resources (funds, entities, accounts)
- Performing irreversible operations
- Actions that could lead to data loss
- Important decisions that need explicit consent

❌ **Don't use ConfirmDialog for:**
- Complex forms (use `FormModal` instead)
- Multi-step processes
- Read-only information display
- Navigation confirmations (use browser confirmation instead)

### UX Guidelines

1. **Clear Titles**: Use action-oriented titles ("Delete Fund", not "Confirm")
2. **Descriptive Text**: Explain what will happen and any consequences
3. **Consistent Labels**: Use clear, action-specific button labels
4. **Error Variant for Destructive**: Always use `confirmVariant="error"` for delete/remove operations
5. **Loading States**: Always show loading state for async operations

## Examples from Codebase

### Fund Deletion (CompaniesPage)

```tsx
<ConfirmDialog
  open={deleteDialogOpen}
  title="Delete Fund"
  description={`Are you sure you want to delete "${fundToDelete?.name}"? This action cannot be undone.`}
  confirmLabel="Delete"
  cancelLabel="Cancel"
  onConfirm={handleConfirmDelete}
  onCancel={() => setDeleteDialogOpen(false)}
  loading={deleteFundMutation.isPending}
  confirmVariant="error"
/>
```

## Related Components

- **FormModal**: For form submissions and complex data entry
- **DependencyBlockedDialog**: For specialized error cases with dependency information

## Migration Notes

This component replaces `components/ui/ConfirmDialog.tsx`. All functionality has been preserved with improved:
- Type safety
- Documentation
- Accessibility
- Theme integration

