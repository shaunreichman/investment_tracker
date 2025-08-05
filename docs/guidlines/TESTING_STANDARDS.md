# Testing Standards Documentation

## Overview
This document establishes comprehensive testing standards for the React frontend, based on the patterns developed during the FundDetail refactoring. These standards ensure high code quality, maintainability, and confidence in the codebase.

## Testing Philosophy

### 1. Test-Driven Development Principles
- **Test First**: Write tests before implementing features
- **Comprehensive Coverage**: Aim for 90%+ test coverage
- **Isolated Testing**: Each test should be independent and repeatable
- **Fast Execution**: Tests should run quickly for rapid feedback

### 2. Testing Pyramid
```
    /\
   /  \     E2E Tests (Few, Slow)
  /____\    
 /      \   Integration Tests (Some, Medium)
/________\  Unit Tests (Many, Fast)
```

## Component Testing Patterns

### 1. Section Component Testing
```typescript
// Example: EquitySection.test.tsx
import { render, screen } from '@testing-library/react';
import { EquitySection } from './EquitySection';

describe('EquitySection', () => {
  const mockFund = {
    id: 1,
    name: 'Test Fund',
    current_equity_balance: 100000,
    average_equity_balance: 95000,
    tracking_type: 'cost_based',
    currency: 'AUD'
  };

  const mockFormatCurrency = jest.fn((amount) => `$${amount}`);
  const mockFormatDate = jest.fn((date) => date);

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
    expect(screen.getByText('Average Balance')).toBeInTheDocument();
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
    expect(screen.queryByText('Current Balance')).not.toBeInTheDocument();
  });

  it('should call formatCurrency with correct parameters', () => {
    render(
      <EquitySection
        fund={mockFund}
        formatCurrency={mockFormatCurrency}
        formatDate={mockFormatDate}
      />
    );

    expect(mockFormatCurrency).toHaveBeenCalledWith(100000, 'AUD');
    expect(mockFormatCurrency).toHaveBeenCalledWith(95000, 'AUD');
  });
});
```

### 2. Table Component Testing
```typescript
// Example: TableContainer.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { TableContainer } from './TableContainer';

describe('TableContainer', () => {
  const mockFund = { id: 1, name: 'Test Fund', tracking_type: 'cost_based' };
  const mockEvents = [
    { id: 1, event_type: 'CAPITAL_CALL', amount: 100000, event_date: '2023-01-01' },
    { id: 2, event_type: 'DISTRIBUTION', amount: 5000, event_date: '2023-06-30' }
  ];

  const mockHandlers = {
    onEventCreated: jest.fn(),
    onEventUpdated: jest.fn(),
    onEventDeleted: jest.fn()
  };

  it('should render table with events', () => {
    render(
      <TableContainer
        fund={mockFund}
        events={mockEvents}
        {...mockHandlers}
      />
    );

    expect(screen.getByText('Capital Call')).toBeInTheDocument();
    expect(screen.getByText('Distribution')).toBeInTheDocument();
  });

  it('should toggle tax events filter', () => {
    render(
      <TableContainer
        fund={mockFund}
        events={mockEvents}
        {...mockHandlers}
      />
    );

    const taxEventsToggle = screen.getByLabelText('Show Tax Events');
    fireEvent.click(taxEventsToggle);

    // Verify filter state changes
    expect(taxEventsToggle).not.toBeChecked();
  });

  it('should call onEventCreated when add event is clicked', () => {
    render(
      <TableContainer
        fund={mockFund}
        events={mockEvents}
        {...mockHandlers}
      />
    );

    const addButton = screen.getByText('Add Event');
    fireEvent.click(addButton);

    // Verify modal opens or handler is called
    expect(mockHandlers.onEventCreated).toHaveBeenCalled();
  });
});
```

### 3. Custom Hook Testing
```typescript
// Example: useEventGrouping.test.ts
import { renderHook } from '@testing-library/react';
import { useEventGrouping } from './useEventGrouping';

describe('useEventGrouping', () => {
  const mockEvents = [
    { id: 1, event_type: 'CAPITAL_CALL', event_date: '2023-01-01' },
    { id: 2, event_type: 'DISTRIBUTION', event_date: '2023-01-01' },
    { id: 3, event_type: 'TAX_PAYMENT', event_date: '2023-06-30' }
  ];

  it('should group events by date correctly', () => {
    const { result } = renderHook(() => 
      useEventGrouping(mockEvents, true, true)
    );

    expect(result.current.groupedEvents).toHaveLength(2);
    expect(result.current.totalEvents).toBe(3);
  });

  it('should filter tax events when showTaxEvents is false', () => {
    const { result } = renderHook(() => 
      useEventGrouping(mockEvents, false, true)
    );

    const taxEvents = result.current.groupedEvents.flat().filter(
      event => event.event_type === 'TAX_PAYMENT'
    );
    expect(taxEvents).toHaveLength(0);
  });

  it('should combine interest and withholding tax events', () => {
    const eventsWithInterest = [
      { id: 1, event_type: 'DISTRIBUTION', distribution_type: 'INTEREST', event_date: '2023-06-30' },
      { id: 2, event_type: 'TAX_PAYMENT', tax_payment_type: 'EOFY_INTEREST_TAX', event_date: '2023-06-30' }
    ];

    const { result } = renderHook(() => 
      useEventGrouping(eventsWithInterest, true, true)
    );

    expect(result.current.groupedEvents).toHaveLength(1);
    const groupedEvent = result.current.groupedEvents[0];
    expect(groupedEvent.events).toHaveLength(2);
  });
});
```

## Integration Testing Patterns

### 1. User Workflow Testing
```typescript
// Example: FundDetail.integration.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FundDetail } from './FundDetail';

describe('FundDetail Integration', () => {
  it('should create, edit, and delete events', async () => {
    render(<FundDetail fundId={1} />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Test Fund')).toBeInTheDocument();
    });

    // Add new event
    const addButton = screen.getByText('Add Event');
    fireEvent.click(addButton);

    // Fill out form
    const amountInput = screen.getByLabelText('Amount');
    fireEvent.change(amountInput, { target: { value: '50000' } });

    const submitButton = screen.getByText('Create Event');
    fireEvent.click(submitButton);

    // Verify event was created
    await waitFor(() => {
      expect(screen.getByText('$50,000')).toBeInTheDocument();
    });

    // Edit event
    const editButton = screen.getByLabelText('Edit event');
    fireEvent.click(editButton);

    // Update amount
    const editAmountInput = screen.getByDisplayValue('50000');
    fireEvent.change(editAmountInput, { target: { value: '75000' } });

    const updateButton = screen.getByText('Update Event');
    fireEvent.click(updateButton);

    // Verify event was updated
    await waitFor(() => {
      expect(screen.getByText('$75,000')).toBeInTheDocument();
    });

    // Delete event
    const deleteButton = screen.getByLabelText('Delete event');
    fireEvent.click(deleteButton);

    const confirmButton = screen.getByText('Delete');
    fireEvent.click(confirmButton);

    // Verify event was deleted
    await waitFor(() => {
      expect(screen.queryByText('$75,000')).not.toBeInTheDocument();
    });
  });
});
```

### 2. API Integration Testing
```typescript
// Example: API integration test
import { render, screen, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { FundDetail } from './FundDetail';

const server = setupServer(
  rest.get('/api/funds/:id', (req, res, ctx) => {
    return res(
      ctx.json({
        id: 1,
        name: 'Test Fund',
        current_equity_balance: 100000
      })
    );
  }),
  rest.post('/api/funds/:id/events', (req, res, ctx) => {
    return res(
      ctx.json({
        id: 1,
        event_type: 'CAPITAL_CALL',
        amount: 50000
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('FundDetail API Integration', () => {
  it('should load fund data and display it', async () => {
    render(<FundDetail fundId={1} />);

    await waitFor(() => {
      expect(screen.getByText('Test Fund')).toBeInTheDocument();
      expect(screen.getByText('$100,000')).toBeInTheDocument();
    });
  });

  it('should handle API errors gracefully', async () => {
    server.use(
      rest.get('/api/funds/:id', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(<FundDetail fundId={1} />);

    await waitFor(() => {
      expect(screen.getByText('Error loading fund data')).toBeInTheDocument();
    });
  });
});
```

## Utility Testing Patterns

### 1. Formatter Testing
```typescript
// Example: formatters.test.ts
import { formatCurrency, formatDate, formatBrokerageFee } from './formatters';

describe('formatters', () => {
  describe('formatCurrency', () => {
    it('should format positive amounts correctly', () => {
      expect(formatCurrency(1000, 'AUD')).toBe('$1,000.00');
      expect(formatCurrency(1000000, 'AUD')).toBe('$1,000,000.00');
    });

    it('should format negative amounts with parentheses', () => {
      expect(formatCurrency(-1000, 'AUD')).toBe('($1,000.00)');
    });

    it('should handle null and undefined values', () => {
      expect(formatCurrency(null, 'AUD')).toBe('$0.00');
      expect(formatCurrency(undefined, 'AUD')).toBe('$0.00');
    });

    it('should support different currencies', () => {
      expect(formatCurrency(1000, 'USD')).toBe('$1,000.00');
      expect(formatCurrency(1000, 'EUR')).toBe('€1,000.00');
    });
  });

  describe('formatDate', () => {
    it('should format dates correctly', () => {
      expect(formatDate('2023-01-01')).toBe('01/01/2023');
      expect(formatDate('2023-12-31')).toBe('31/12/2023');
    });

    it('should handle null and undefined values', () => {
      expect(formatDate(null)).toBe('');
      expect(formatDate(undefined)).toBe('');
    });
  });
});
```

### 2. Validator Testing
```typescript
// Example: validators.test.ts
import { validateField, createValidator } from './validators';

describe('validators', () => {
  describe('validateField', () => {
    it('should validate required fields', () => {
      expect(validateField('', 'required')).toBe('This field is required');
      expect(validateField('test', 'required')).toBe('');
    });

    it('should validate amounts', () => {
      expect(validateField('100', 'amount')).toBe('');
      expect(validateField('-100', 'amount')).toBe('');
      expect(validateField('abc', 'amount')).toBe('Must be a valid number');
      expect(validateField('0', 'amount')).toBe('Amount must be greater than 0');
    });

    it('should validate dates', () => {
      expect(validateField('2023-01-01', 'date')).toBe('');
      expect(validateField('invalid', 'date')).toBe('Must be a valid date');
    });
  });

  describe('createValidator', () => {
    it('should create custom validators', () => {
      const customValidator = createValidator([
        { rule: 'required', message: 'Name is required' },
        { rule: 'minLength', value: 3, message: 'Name must be at least 3 characters' }
      ]);

      expect(customValidator('')).toBe('Name is required');
      expect(customValidator('ab')).toBe('Name must be at least 3 characters');
      expect(customValidator('abc')).toBe('');
    });
  });
});
```

## Test Organization

### 1. File Structure
```
src/
├── components/
│   ├── fund-detail/
│   │   ├── EquitySection.tsx
│   │   ├── EquitySection.test.tsx
│   │   ├── FundDetailTable/
│   │   │   ├── TableContainer.tsx
│   │   │   ├── TableContainer.test.tsx
│   │   │   ├── useEventGrouping.ts
│   │   │   └── useEventGrouping.test.ts
│   │   └── index.ts
│   └── modals/
│       ├── CreateFundEventModal.tsx
│       └── CreateFundEventModal.test.tsx
├── utils/
│   ├── formatters.ts
│   ├── formatters.test.ts
│   ├── validators.ts
│   ├── validators.test.ts
│   ├── helpers.ts
│   ├── helpers.test.ts
│   ├── constants.ts
│   └── constants.test.ts
└── __tests__/
    ├── integration/
    │   └── FundDetail.integration.test.tsx
    └── setup/
        └── test-utils.tsx
```

### 2. Test Naming Conventions
- **Unit Tests**: `ComponentName.test.tsx`
- **Integration Tests**: `ComponentName.integration.test.tsx`
- **Utility Tests**: `utilityName.test.ts`
- **Hook Tests**: `useHookName.test.ts`

## Test Setup and Configuration

### 1. Test Utilities
```typescript
// Example: test-utils.tsx
import { render, RenderOptions } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { theme } from '../theme';

const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <ThemeProvider theme={theme}>
      {children}
    </ThemeProvider>
  );
};

const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };
```

### 2. Mock Data Factories
```typescript
// Example: mock-data.ts
export const createMockFund = (overrides = {}) => ({
  id: 1,
  name: 'Test Fund',
  current_equity_balance: 100000,
  average_equity_balance: 95000,
  tracking_type: 'cost_based',
  currency: 'AUD',
  ...overrides
});

export const createMockEvent = (overrides = {}) => ({
  id: 1,
  event_type: 'CAPITAL_CALL',
  amount: 100000,
  event_date: '2023-01-01',
  description: 'Test event',
  ...overrides
});
```

## Coverage Requirements

### 1. Coverage Targets
- **Statements**: 90%+
- **Branches**: 85%+
- **Functions**: 90%+
- **Lines**: 90%+

### 2. Coverage Exclusions
- **Test files**: Exclude all `.test.tsx` and `.test.ts` files
- **Setup files**: Exclude test setup and utility files
- **Type definitions**: Exclude `.d.ts` files
- **Build artifacts**: Exclude `dist/` and `build/` directories

### 3. Coverage Reporting
```json
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.test.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/test-utils.tsx'
  ],
  coverageThreshold: {
    global: {
      statements: 90,
      branches: 85,
      functions: 90,
      lines: 90
    }
  }
};
```

## Performance Testing

### 1. Render Performance Testing
```typescript
// Example: performance.test.tsx
import { render } from '@testing-library/react';
import { FundDetail } from './FundDetail';

describe('FundDetail Performance', () => {
  it('should render within performance budget', () => {
    const startTime = performance.now();
    
    render(<FundDetail fundId={1} />);
    
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    // Should render in under 100ms
    expect(renderTime).toBeLessThan(100);
  });

  it('should handle large datasets efficiently', () => {
    const largeEventSet = Array.from({ length: 1000 }, (_, i) => ({
      id: i,
      event_type: 'CAPITAL_CALL',
      amount: 1000,
      event_date: '2023-01-01'
    }));

    const startTime = performance.now();
    
    render(<FundDetail fundId={1} events={largeEventSet} />);
    
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    // Should render large datasets in under 500ms
    expect(renderTime).toBeLessThan(500);
  });
});
```

## Debugging and Troubleshooting

### 1. Test Debugging
```typescript
// Enable debug logging in tests
import { debug } from '@testing-library/react';

describe('Component Debugging', () => {
  it('should debug component state', () => {
    const { container } = render(<MyComponent />);
    
    // Log the entire component tree
    debug(container);
    
    // Or log specific elements
    debug(screen.getByText('Some text'));
  });
});
```

### 2. Debug Infrastructure
```typescript
// Example: debug.ts
export const debugTableRendering = (events: FundEvent[], groupedEvents: any[]) => {
  console.log('Original events:', events);
  console.log('Grouped events:', groupedEvents);
  console.log('Event count:', events.length);
  console.log('Group count:', groupedEvents.length);
};

export const compareTableRendering = (before: any, after: any) => {
  console.log('Before rendering:', before);
  console.log('After rendering:', after);
  console.log('Differences:', JSON.stringify(before) !== JSON.stringify(after));
};
```

## Best Practices

### 1. Test Organization
- **Arrange**: Set up test data and conditions
- **Act**: Perform the action being tested
- **Assert**: Verify the expected outcome

### 2. Test Isolation
- Each test should be independent
- Clean up after each test
- Use fresh data for each test

### 3. Meaningful Assertions
- Test behavior, not implementation
- Use descriptive test names
- Test edge cases and error conditions

### 4. Performance Considerations
- Keep tests fast
- Mock expensive operations
- Use efficient test data

## Continuous Integration

### 1. CI Pipeline
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test -- --coverage
      - run: npm run test:integration
      - run: npm run test:performance
```

### 2. Quality Gates
- All tests must pass
- Coverage thresholds must be met
- No new linting errors
- Performance budgets maintained

This testing framework ensures high code quality, maintainability, and confidence in the codebase while supporting rapid development and team collaboration. 