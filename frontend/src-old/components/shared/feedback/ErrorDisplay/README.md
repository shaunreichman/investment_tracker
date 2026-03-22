# ErrorDisplay Component

Enterprise-grade error display component with retry logic, auto-dismiss, and technical details.

## Overview

`ErrorDisplay` is a comprehensive, refactored error display component that provides:
- **Modular Architecture**: Broken into focused sub-components
- **Hook Integration**: Leverages `useErrorHandler` for retry logic
- **Accessibility**: Full ARIA support and semantic HTML
- **Flexibility**: Multiple display modes and customization options
- **Type Safety**: Full TypeScript coverage

## Architecture

### Component Structure
```
ErrorDisplay/
├── ErrorDisplay.tsx          # Main container component
├── ErrorDisplay.types.ts     # Type definitions
├── utils.ts                  # Helper functions (icons, colors)
├── components/
│   ├── ErrorHeader.tsx       # Header with badges and actions
│   ├── ErrorMessage.tsx      # User-friendly message
│   ├── ErrorDetails.tsx      # Collapsible technical details
│   ├── ErrorMetadata.tsx     # Metadata chips
│   ├── ErrorRetry.tsx        # Retry button and status
│   └── index.ts             # Barrel export
└── index.ts                 # Main barrel export
```

### Design Principles
- **Container Pattern**: Main component orchestrates, sub-components present
- **Separation of Concerns**: Each sub-component has single responsibility
- **Reusability**: Sub-components can be used independently
- **Performance**: All sub-components use `React.memo`
- **Hooks-First**: Logic extracted into reusable hooks

## Usage

### Basic Usage
```tsx
import { ErrorDisplay } from '@/components/shared/feedback';

<ErrorDisplay
  error={error}
  onDismiss={() => setError(null)}
/>
```

### With Retry
```tsx
<ErrorDisplay
  error={error}
  onRetry={async () => {
    await refetch();
  }}
  maxRetries={3}
  onDismiss={() => setError(null)}
/>
```

### With Auto-Dismiss
```tsx
<ErrorDisplay
  error={error}
  autoDismiss
  dismissDelay={5000}
  onDismiss={() => setError(null)}
/>
```

### With Technical Details
```tsx
<ErrorDisplay
  error={error}
  showDetails
  showErrorId
  canDismiss
  onDismiss={() => setError(null)}
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `error` | `ErrorInfo \| null` | - | Error information to display |
| `showDetails` | `boolean` | `false` | Show technical details initially |
| `canDismiss` | `boolean` | `true` | Allow error dismissal |
| `autoDismiss` | `boolean` | `false` | Auto-dismiss after delay |
| `dismissDelay` | `number` | `5000` | Auto-dismiss delay (ms) |
| `maxRetries` | `number` | `3` | Maximum retry attempts |
| `onRetry` | `() => void \| Promise<void>` | - | Retry callback (enables retry if error is retryable) |
| `onDismiss` | `() => void` | - | Dismiss callback |
| `onToggleDetails` | `(show: boolean) => void` | - | Details toggle callback |
| `customMessage` | `string` | - | Override error message |
| `showErrorId` | `boolean` | `false` | Show error ID for debugging |
| `sx` | `SxProps` | `{}` | Custom MUI styling |

**Note**: Retry functionality is automatically determined by `error.retryable`. If the error is retryable and `onRetry` is provided, the retry button will appear.

## Sub-Components

### ErrorHeader
Displays error type, severity badges, and action buttons.

```tsx
import { ErrorHeader } from '@/components/shared/feedback';

<ErrorHeader
  error={error}
  showDetails={showDetails}
  hasTechnicalDetails={true}
  canDismiss={true}
  onToggleDetails={toggleDetails}
  onDismiss={handleDismiss}
/>
```

### ErrorMessage
Pure presentational component for user-friendly message.

```tsx
import { ErrorMessage } from '@/components/shared/feedback';

<ErrorMessage message="Failed to load data. Please try again." />
```

### ErrorDetails
Collapsible technical details with stack trace.

```tsx
import { ErrorDetails } from '@/components/shared/feedback';

<ErrorDetails error={error} show={showDetails} />
```

### ErrorRetry
Retry button with status indicator.

```tsx
import { ErrorRetry } from '@/components/shared/feedback';

// Note: Typically used internally by ErrorDisplay
// but can be used standalone for custom error UIs
<ErrorRetry
  canRetry={true}
  isRetrying={false}
  retryCount={1}
  maxRetries={3}
  onRetry={handleRetry}
/>
```

### ErrorMetadata
Metadata chips for debugging information.

```tsx
import { ErrorMetadata } from '@/components/shared/feedback';

<ErrorMetadata error={error} />
```

## Hooks Used

### useErrorHandler
Core error handling hook with retry logic.

```tsx
import { useErrorHandler } from '@/hooks/core/error';

const { isRetrying, canRetry, retry } = useErrorHandler({ maxRetries: 3 });
```

### useErrorAutoDismiss
Auto-dismiss functionality.

```tsx
import { useErrorAutoDismiss } from '@/hooks/ui';

useErrorAutoDismiss(autoDismiss, 5000, handleDismiss, error);
```

### useErrorDetailsToggle
Technical details visibility toggle.

```tsx
import { useErrorDetailsToggle } from '@/hooks/ui';

const { showDetails, toggleDetails } = useErrorDetailsToggle(false);
```

## Error Types

The component works with `ErrorInfo` from `@/types/errors`:

```typescript
interface ErrorInfo {
  id?: string;
  type: ErrorType;
  severity: ErrorSeverity;
  message: string;
  userMessage: string;
  code?: number;
  timestamp: Date;
  retryable: boolean;
  stack?: string;
  details?: Record<string, any>;
}
```

## Accessibility

- `role="alert"` on Alert component
- ARIA labels on all interactive elements
- Keyboard navigation support
- Screen reader friendly
- Proper focus management

## Performance

- All sub-components use `React.memo`
- Event handlers memoized with `useCallback`
- No unnecessary re-renders
- Efficient state updates

## Examples

### API Error with Retry
```tsx
const { error, isRetrying } = useErrorHandler();

<ErrorDisplay
  error={error}
  onRetry={async () => {
    await apiClient.refetch();
  }}
  onDismiss={() => clearError()}
  maxRetries={5}
/>
```

### Form Validation Error
```tsx
<ErrorDisplay
  error={{
    type: ErrorType.VALIDATION,
    severity: ErrorSeverity.MEDIUM,
    message: 'Validation failed',
    userMessage: 'Please check your inputs and try again.',
    retryable: false,
    timestamp: new Date(),
  }}
  canDismiss
  onDismiss={() => setFormError(null)}
/>
```

### Network Error with Auto-Dismiss
```tsx
<ErrorDisplay
  error={networkError}
  autoDismiss
  dismissDelay={3000}
  onRetry={refetch}
  onDismiss={() => setNetworkError(null)}
/>
```

## Testing

All components are designed for easy testing:

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorDisplay } from './ErrorDisplay';

test('displays error message', () => {
  const error = {
    type: ErrorType.NETWORK,
    severity: ErrorSeverity.HIGH,
    message: 'Network error',
    userMessage: 'Connection failed',
    retryable: true,
    timestamp: new Date(),
  };
  
  render(<ErrorDisplay error={error} />);
  expect(screen.getByText('Connection failed')).toBeInTheDocument();
});

test('calls onRetry when retry button clicked', () => {
  const onRetry = jest.fn();
  render(<ErrorDisplay error={retryableError} onRetry={onRetry} />);
  
  fireEvent.click(screen.getByText('Retry'));
  expect(onRetry).toHaveBeenCalled();
});
```

## Migration from Old ErrorDisplay

The refactored component has a cleaner API:

| Old Prop | New Prop | Migration Notes |
|----------|----------|-----------------|
| `error` | `error` | ✅ No change |
| `showDetails` | `showDetails` | ✅ No change |
| `canRetry` | - | ❌ Removed - automatically determined by `error.retryable` |
| `isRetrying` | - | ❌ Removed - managed internally by `useErrorHandler` |
| `retryCount` | - | ❌ Removed - managed internally by `useErrorHandler` |
| `variant` | - | ❌ Removed - not implemented |
| `canDismiss` | `canDismiss` | ✅ No change |
| `autoDismiss` | `autoDismiss` | ✅ No change |
| `dismissDelay` | `dismissDelay` | ✅ No change |
| `maxRetries` | `maxRetries` | ✅ No change |
| `onRetry` | `onRetry` | ✅ No change |
| `onDismiss` | `onDismiss` | ✅ No change |

### Migration Example

**Before:**
```tsx
<ErrorDisplay
  error={error}
  canRetry={error.retryable}    // Remove - automatic now
  isRetrying={isRetrying}        // Remove - internal state
  retryCount={retryCount}        // Remove - internal state
  variant="inline"               // Remove - not used
  onRetry={handleRetry}
  onDismiss={handleDismiss}
/>
```

**After:**
```tsx
<ErrorDisplay
  error={error}                  // Just pass the error
  onRetry={handleRetry}          // Retry shows if error.retryable
  onDismiss={handleDismiss}
/>
```

## Benefits of Refactored Version

1. **Reduced Complexity**: 444 lines → ~150 lines main component + small sub-components
2. **Better Testing**: Each component can be tested independently
3. **Improved Performance**: Memoized sub-components reduce re-renders
4. **Hook Integration**: Leverages `useErrorHandler` for consistent behavior
5. **Maintainability**: Clear component boundaries and responsibilities
6. **Extensibility**: Easy to add new features or customize behavior

