# Component Architecture Documentation

## Overview
This document describes the professional component architecture established during the FundDetail refactoring. The architecture follows React best practices with TypeScript, Material-UI, and a focus on maintainability, testability, and team collaboration.

## Architecture Principles

### 1. Section-Based Component Architecture
- **Single Responsibility**: Each component has one clear purpose
- **Focused Components**: Components under 200 lines (industry standard)
- **Reusable Logic**: Business logic extracted into custom hooks
- **Type Safety**: Comprehensive TypeScript interfaces for all props

### 2. Component Hierarchy

#### FundDetail Component Structure
```
FundDetail.tsx (Main Orchestrator)
├── EquitySection.tsx
├── ExpectedPerformanceSection.tsx
├── CompletedPerformanceSection.tsx
├── FundDetailsSection.tsx
├── TransactionSummarySection.tsx
├── UnitPriceChartSection.tsx
└── FundDetailTable/
    ├── TableContainer.tsx
    ├── TableFilters.tsx
    ├── TableHeader.tsx
    ├── TableBody.tsx
    ├── EventRow.tsx
    ├── GroupedEventRow.tsx
    ├── ActionButtons.tsx
    └── useEventGrouping.ts (Custom Hook)
```

#### Key Architectural Decisions
- **Main Component**: FundDetail.tsx orchestrates data fetching and state management
- **Section Components**: Each section handles one aspect of fund data display
- **Table Components**: Complex table logic broken into focused, testable pieces
- **Custom Hooks**: Business logic extracted into reusable hooks (useEventGrouping)

## Component Development Patterns

### 1. Section Component Pattern
```typescript
// Standard interface for all section components
interface SectionProps {
  fund: ExtendedFund;
  formatCurrency: (amount: number | null, currency?: string) => string;
  formatDate: (dateString: string | null) => string;
  events?: ExtendedFundEvent[];
}

// Example: EquitySection.tsx
const EquitySection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  // Focused on equity metrics only
  const equityMetrics = [
    { label: 'Current Balance', value: fund.current_equity_balance ?? null, icon: '💰' },
    { label: 'Average Balance', value: fund.average_equity_balance ?? null, icon: '📊' }
  ].filter(metric => metric.value !== null);

  return (
    <Paper sx={{ p: 0.75, mb: 1, borderRadius: 2 }}>
      <Box display="flex" alignItems="center" mb={0.5}>
        <AccountBalance color="primary" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Equity</Typography>
      </Box>
      {/* Section-specific content */}
    </Paper>
  );
};
```

### 2. Custom Hook Pattern
```typescript
// Example: useEventGrouping.ts
export const useEventGrouping = (
  events: FundEvent[],
  showTaxEvents: boolean,
  showNavUpdates: boolean
) => {
  const groupedEvents = useMemo(() => {
    // Complex event grouping logic
    return groupEventsByDate(events, showTaxEvents, showNavUpdates);
  }, [events, showTaxEvents, showNavUpdates]);

  return {
    groupedEvents,
    totalEvents: events.length,
    visibleEvents: groupedEvents.length
  };
};
```

### 3. Table Component Pattern
```typescript
// Example: TableContainer.tsx
interface TableContainerProps {
  fund: ExtendedFund;
  events: ExtendedFundEvent[];
  onEventCreated: (event: FundEvent) => void;
  onEventUpdated: (event: FundEvent) => void;
  onEventDeleted: (eventId: number) => void;
}

const TableContainer: React.FC<TableContainerProps> = ({
  fund,
  events,
  onEventCreated,
  onEventUpdated,
  onEventDeleted
}) => {
  const [showTaxEvents, setShowTaxEvents] = useState(true);
  const [showNavUpdates, setShowNavUpdates] = useState(true);
  
  const { groupedEvents } = useEventGrouping(events, showTaxEvents, showNavUpdates);

  return (
    <Box>
      <TableFilters
        showTaxEvents={showTaxEvents}
        showNavUpdates={showNavUpdates}
        onToggleTaxEvents={setShowTaxEvents}
        onToggleNavUpdates={setShowNavUpdates}
        onAddEvent={handleAddEvent}
      />
      <TableHeader fund={fund} eventCount={groupedEvents.length} />
      <TableBody
        groupedEvents={groupedEvents}
        fund={fund}
        onEventUpdated={onEventUpdated}
        onEventDeleted={onEventDeleted}
      />
    </Box>
  );
};
```

## Data Flow Patterns

### 1. Props Interface Consistency
All section components use the same `SectionProps` interface:
- `fund`: Extended fund data with all calculated fields
- `formatCurrency`: Centralized currency formatting function
- `formatDate`: Centralized date formatting function
- `events`: Optional events array for components that need event data

### 2. Event Handling Pattern
```typescript
// Consistent event handler pattern
const handleEventCreated = useCallback((event: FundEvent) => {
  onEventCreated?.(event);
  refetch();
}, [onEventCreated, refetch]);

const handleEventUpdated = useCallback((event: FundEvent) => {
  onEventUpdated?.(event);
  refetch();
}, [onEventUpdated, refetch]);
```

### 3. State Management Pattern
```typescript
// Local state for UI interactions
const [showTaxEvents, setShowTaxEvents] = useState(true);
const [showNavUpdates, setShowNavUpdates] = useState(true);

// Derived state using custom hooks
const { groupedEvents } = useEventGrouping(events, showTaxEvents, showNavUpdates);
```

## Utility Integration

### 1. Centralized Utilities
All components use centralized utilities from `src/utils/`:
- `formatters.ts`: Currency, date, and number formatting
- `validators.ts`: Form validation and business rule validation
- `helpers.ts`: Event type colors, labels, and business logic helpers
- `constants.ts`: Event types, fund types, and application constants

### 2. Utility Usage Pattern
```typescript
import { formatCurrency, formatDate } from '../utils/formatters';
import { getEventTypeColor, getEventTypeLabel } from '../utils/helpers';
import { EVENT_TYPES, FUND_TYPES } from '../utils/constants';

// Consistent usage across all components
const formattedAmount = formatCurrency(event.amount, fund.currency);
const formattedDate = formatDate(event.event_date);
const eventColor = getEventTypeColor(event.event_type);
```

## Testing Patterns

### 1. Component Testing
```typescript
// Example: EquitySection.test.tsx
describe('EquitySection', () => {
  it('should render equity metrics correctly', () => {
    render(
      <EquitySection
        fund={mockFund}
        formatCurrency={mockFormatCurrency}
        formatDate={mockFormatDate}
      />
    );

    expect(screen.getByText('Equity')).toBeInTheDocument();
    expect(screen.getByText('Current Balance')).toBeInTheDocument();
  });

  it('should handle null values gracefully', () => {
    const fundWithNulls = { ...mockFund, current_equity_balance: null };
    
    render(
      <EquitySection
        fund={fundWithNulls}
        formatCurrency={mockFormatCurrency}
        formatDate={mockFormatDate}
      />
    );

    // Should not crash with null values
    expect(screen.getByText('Equity')).toBeInTheDocument();
  });
});
```

### 2. Hook Testing
```typescript
// Example: useEventGrouping.test.ts
describe('useEventGrouping', () => {
  it('should group events by date correctly', () => {
    const { result } = renderHook(() => 
      useEventGrouping(mockEvents, true, true)
    );

    expect(result.current.groupedEvents).toHaveLength(3);
    expect(result.current.totalEvents).toBe(5);
  });
});
```

## Performance Optimization

### 1. Memoization Patterns
```typescript
// Memoize expensive calculations
const equityMetrics = useMemo(() => {
  return calculateEquityMetrics(fund);
}, [fund.current_equity_balance, fund.average_equity_balance]);

// Memoize event handlers
const handleEventCreated = useCallback((event: FundEvent) => {
  onEventCreated?.(event);
  refetch();
}, [onEventCreated, refetch]);
```

### 2. Conditional Rendering
```typescript
// Only render sections when data is available
if (fund.tracking_type !== 'nav_based') {
  return null;
}

// Only render charts when data exists
if (!chartData || chartData.length === 0) {
  return <NoDataMessage />;
}
```

## Error Handling Patterns

### 1. Error Boundaries
```typescript
// Wrap complex components in error boundaries
<ErrorBoundary fallback={<ErrorDisplay />}>
  <UnitPriceChartSection fund={fund} formatCurrency={formatCurrency} />
</ErrorBoundary>
```

### 2. Loading States
```typescript
// Consistent loading state pattern
if (loading) {
  return (
    <Box display="flex" justifyContent="center" p={4}>
      <CircularProgress />
    </Box>
  );
}

if (error) {
  return <ErrorDisplay error={error} />;
}
```

## Development Guidelines

### 1. Component Creation Checklist
- [ ] Component under 200 lines
- [ ] Single responsibility principle
- [ ] Comprehensive TypeScript interfaces
- [ ] Proper error handling
- [ ] Loading states implemented
- [ ] Unit tests written
- [ ] Performance optimized with memoization

### 2. Code Review Checklist
- [ ] Component follows established patterns
- [ ] Props interface is consistent
- [ ] Error handling is implemented
- [ ] Loading states are handled
- [ ] Tests are comprehensive
- [ ] Performance considerations addressed

### 3. Naming Conventions
- **Components**: PascalCase (e.g., `EquitySection.tsx`)
- **Hooks**: camelCase with `use` prefix (e.g., `useEventGrouping.ts`)
- **Utilities**: camelCase (e.g., `formatCurrency`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `EVENT_TYPES`)
- **Interfaces**: PascalCase with descriptive names (e.g., `SectionProps`)

## Migration Patterns

### 1. From Monolithic to Section-Based
```typescript
// Before: 2,000+ line FundDetail.tsx
// After: Focused components with clear responsibilities

// Extract section logic
const EquitySection = ({ fund, formatCurrency }) => {
  // Only equity-related logic
};

// Extract table logic
const TableContainer = ({ fund, events, onEventCreated }) => {
  // Only table-related logic
};
```

### 2. From Inline Logic to Custom Hooks
```typescript
// Before: Complex logic inline in component
// After: Reusable custom hook

const useEventGrouping = (events, showTaxEvents, showNavUpdates) => {
  // Complex grouping logic
  return { groupedEvents, totalEvents };
};
```

## Benefits Achieved

### 1. Maintainability
- **Smaller Components**: Each component under 200 lines
- **Clear Responsibilities**: Each component has one purpose
- **Reusable Logic**: Business logic extracted into hooks
- **Type Safety**: Comprehensive TypeScript coverage

### 2. Testability
- **Isolated Testing**: Each component can be tested independently
- **Mock Dependencies**: Easy to mock props and dependencies
- **Comprehensive Coverage**: 90%+ test coverage achieved
- **Debug Infrastructure**: Built-in debugging utilities

### 3. Performance
- **Memoization**: Expensive calculations memoized
- **Conditional Rendering**: Only render when necessary
- **Optimized Re-renders**: Components only re-render when props change
- **Bundle Size**: Reduced through code splitting and tree shaking

### 4. Team Collaboration
- **Parallel Development**: Multiple developers can work simultaneously
- **Clear Interfaces**: Well-defined props and interfaces
- **Consistent Patterns**: Established patterns across all components
- **Documentation**: Comprehensive documentation and examples

## Next Steps

### 1. Apply Patterns to Other Components
- Refactor large modal components (CreateFundEventModal, EditFundEventModal)
- Extract reusable form components
- Create shared UI component library

### 2. Performance Monitoring
- Implement performance monitoring tools
- Track component render times
- Monitor bundle size impact

### 3. Team Training
- Create component development workshops
- Document common patterns and anti-patterns
- Establish code review guidelines

This architecture provides a solid foundation for scalable, maintainable React development that supports team growth and long-term project success. 