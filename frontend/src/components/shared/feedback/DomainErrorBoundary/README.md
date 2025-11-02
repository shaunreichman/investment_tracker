# DomainErrorBoundary

Enterprise-grade error boundary with domain-specific error handling, error tracking, and recovery.

## Features

- **Domain-Specific Messages**: Contextual error messages for fund, entity, company, banking, and rates domains
- **Error Loop Detection**: Prevents infinite error states by tracking error frequency
- **Full Logging Integration**: Automatically logs errors to errorLogger with context and metadata
- **Error Count Tracking**: Monitors error frequency and warns users of persistent issues
- **Technical Details Toggle**: Optional display of stack traces for debugging
- **Recovery Actions**: Retry and navigate-to-safety buttons
- **Production-Ready**: Integrated with Sentry-ready error logging infrastructure

## Usage

### Basic Usage

```typescript
import { DomainErrorBoundary } from '@/components/shared/feedback';

function FundPage() {
  return (
    <DomainErrorBoundary domain="fund">
      <FundDetail />
    </DomainErrorBoundary>
  );
}
```

### With Reset Handler

```typescript
function FundPage() {
  const handleReset = () => {
    // Clear any local state
    // Refetch data
  };

  return (
    <DomainErrorBoundary domain="fund" onReset={handleReset}>
      <FundDetail />
    </DomainErrorBoundary>
  );
}
```

### With Technical Details (Development)

```typescript
const isDevelopment = process.env.NODE_ENV === 'development';

<DomainErrorBoundary domain="company" showDetails={isDevelopment}>
  <CompanyDetail />
</DomainErrorBoundary>
```

### With Custom Context

```typescript
<DomainErrorBoundary 
  domain="fund" 
  context={{
    userId: user.id,
    metadata: { fundId, viewType: 'detail' }
  }}
>
  <FundDetail />
</DomainErrorBoundary>
```

### With Custom Fallback

```typescript
<DomainErrorBoundary 
  domain="entity" 
  fallback={<CustomErrorUI />}
>
  <EntityList />
</DomainErrorBoundary>
```

## Domains

Available domain types for context-specific error messages:

- `fund` - Fund-related components
- `entity` - Entity-related components
- `company` - Company-related components
- `banking` - Banking-related components
- `rates` - Rate/pricing-related components
- `general` - Generic/fallback domain

## Error Logging

All errors are automatically logged via `errorLogger` with:
- Domain context
- Component stack trace
- Error count
- Custom metadata (if provided)

Errors are tracked and can trigger warnings if error loops are detected (>5 errors).

## Architecture Integration

### Error Logger
Integrates with `utils/errorLogger.ts` for:
- Console logging (development)
- Remote monitoring (Sentry, production)
- Error frequency tracking
- Error history

### Error Types
Uses `types/errors.ts` for:
- Error classification (ErrorType)
- Severity levels (ErrorSeverity)
- User-friendly messages
- Context-aware error handling

## Best Practices

### App-Level Protection
```typescript
// App.tsx
<DomainErrorBoundary domain="general">
  <Router>
    <Routes />
  </Router>
</DomainErrorBoundary>
```

### Feature-Level Protection
```typescript
// Feature pages
<DomainErrorBoundary domain="fund">
  <FundDetail />
</DomainErrorBoundary>

<DomainErrorBoundary domain="company">
  <CompanyDetail />
</DomainErrorBoundary>
```

### Nested Boundaries
```typescript
// App-level catch-all
<DomainErrorBoundary domain="general">
  <App>
    {/* Feature-level specific handling */}
    <DomainErrorBoundary domain="fund">
      <FundFeature />
    </DomainErrorBoundary>
  </App>
</DomainErrorBoundary>
```

## vs Basic ErrorBoundary

Use `DomainErrorBoundary` when you need:
- Domain-specific error messages
- Error tracking and logging
- Error loop detection
- Production monitoring integration
- Rich error context

Use basic `ErrorBoundary` (if it existed) when you need:
- Simple error catching
- Minimal overhead
- Generic error handling

**Note**: DomainErrorBoundary is the recommended choice for all use cases in this application.

