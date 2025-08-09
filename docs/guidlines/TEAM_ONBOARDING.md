# Team Onboarding Guide

## Overview
This guide helps new team members quickly understand the project architecture, development patterns, and best practices established during the FundDetail refactoring. It provides practical examples and clear guidelines for contributing to the codebase.

## Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd investment_tracker

# Backend setup
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install

# Start development servers
# Terminal 1: Backend (http://localhost:5001)
source venv/bin/activate
FLASK_APP=src/api.py python -m flask run --host=0.0.0.0 --port=5001

# Terminal 2: Frontend (http://localhost:3000)
cd frontend
npm start
```

### 2. Health Checks
```bash
# Backend health check
curl http://localhost:5001/api/health

# Frontend health check
curl http://localhost:3000
```

## Architecture Overview

### 1. Project Structure
```
investment_tracker/
├── src/                    # Backend (Flask/Python)
│   ├── api.py             # Main API endpoints
│   ├── models.py          # Database models
│   └── calculations.py    # Business logic
├── frontend/              # Frontend (React/TypeScript)
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── utils/         # Shared utilities
│   │   └── services/      # API services
│   └── public/            # Static assets
└── docs/                  # Documentation
```

### 2. Component Architecture
The frontend follows a **section-based architecture** where large components are broken into focused, manageable pieces:

```
FundDetail.tsx (Main Orchestrator)
├── EquitySection.tsx          # Equity metrics
├── ExpectedPerformanceSection.tsx  # Expected performance
├── CompletedPerformanceSection.tsx # Completed performance
├── FundDetailsSection.tsx     # Basic fund info
├── TransactionSummarySection.tsx   # Transaction totals
├── UnitPriceChartSection.tsx  # NAV performance chart
└── FundDetailTable/           # Complex table logic
    ├── TableContainer.tsx     # Table orchestration
    ├── TableFilters.tsx       # Filter controls
    ├── TableHeader.tsx        # Table header
    ├── TableBody.tsx          # Table body
    ├── EventRow.tsx           # Individual event rows
    ├── GroupedEventRow.tsx    # Combined event rows
    ├── ActionButtons.tsx      # Edit/delete buttons
    └── useEventGrouping.ts    # Custom hook for grouping
```

## Development Patterns

### 1. Component Development Pattern
```typescript
// Standard section component pattern
interface SectionProps {
  fund: ExtendedFund;
  formatCurrency: (amount: number | null, currency?: string) => string;
  formatDate: (dateString: string | null) => string;
  events?: ExtendedFundEvent[];
}

const MySection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  // 1. Extract data for this section
  const sectionData = useMemo(() => {
    return calculateSectionData(fund);
  }, [fund]);

  // 2. Handle loading/error states
  if (!sectionData) {
    return <LoadingSpinner />;
  }

  // 3. Render section content
  return (
    <Paper sx={{ p: 0.75, mb: 1, borderRadius: 2 }}>
      <Box display="flex" alignItems="center" mb={0.5}>
        <Icon color="primary" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Section Title</Typography>
      </Box>
      {/* Section-specific content */}
    </Paper>
  );
};
```

### 2. Custom Hook Pattern
```typescript
// Extract complex logic into reusable hooks
export const useMyCustomHook = (data: any[], options: any) => {
  const processedData = useMemo(() => {
    return processData(data, options);
  }, [data, options]);

  const handlers = useCallback(() => {
    // Event handlers
  }, [processedData]);

  return {
    data: processedData,
    handlers,
    isLoading: false,
    error: null
  };
};
```

### 3. Utility Usage Pattern
```typescript
// Always use centralized utilities
import { formatCurrency, formatDate } from '../utils/formatters';
import { getEventTypeColor, getEventTypeLabel } from '../utils/helpers';
import { EVENT_TYPES, FUND_TYPES } from '../utils/constants';

// Consistent usage across components
const formattedAmount = formatCurrency(event.amount, fund.currency);
const formattedDate = formatDate(event.event_date);
const eventColor = getEventTypeColor(event.event_type);
```

## Common Tasks

### 1. Adding a New Section Component
```typescript
// 1. Create the component file
// frontend/src/components/fund-detail/NewSection.tsx
import React from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { SectionProps } from './types';

const NewSection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  return (
    <Paper sx={{ p: 0.75, mb: 1, borderRadius: 2 }}>
      <Typography variant="h6">New Section</Typography>
      {/* Your section content */}
    </Paper>
  );
};

export default NewSection;
```

```typescript
// 2. Add to the main component
// frontend/src/components/fund-detail/index.ts
export { default as NewSection } from './NewSection';

// frontend/src/components/FundDetail.tsx
import { NewSection } from './fund-detail';

// Add to the render method
<NewSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
```

```typescript
// 3. Write tests
// frontend/src/components/fund-detail/NewSection.test.tsx
import { render, screen } from '@testing-library/react';
import NewSection from './NewSection';

describe('NewSection', () => {
  it('should render correctly', () => {
    render(
      <NewSection
        fund={mockFund}
        formatCurrency={mockFormatCurrency}
        formatDate={mockFormatDate}
      />
    );

    expect(screen.getByText('New Section')).toBeInTheDocument();
  });
});
```

### 2. Adding a New Event Type
```typescript
// 1. Add to constants
// frontend/src/utils/constants.ts
export const EVENT_TYPES = {
  // ... existing types
  NEW_EVENT_TYPE: 'NEW_EVENT_TYPE'
} as const;

// 2. Add to helpers
// frontend/src/utils/helpers.ts
export const getEventTypeColor = (eventType: string): string => {
  switch (eventType) {
    // ... existing cases
    case EVENT_TYPES.NEW_EVENT_TYPE:
      return '#4CAF50';
    default:
      return '#757575';
  }
};

export const getEventTypeLabel = (eventType: string): string => {
  switch (eventType) {
    // ... existing cases
    case EVENT_TYPES.NEW_EVENT_TYPE:
      return 'New Event Type';
    default:
      return 'Unknown';
  }
};
```

```typescript
// 3. Update table rendering
// frontend/src/components/fund-detail/FundDetailTable/EventRow.tsx
const renderEventTypeCell = (event: FundEvent) => {
  switch (event.event_type) {
    // ... existing cases
    case EVENT_TYPES.NEW_EVENT_TYPE:
      return (
        <TableCell>
          <Chip
            label={getEventTypeLabel(event.event_type)}
            color="primary"
            size="small"
          />
        </TableCell>
      );
    default:
      return null;
  }
};
```

### 3. Adding a New Form Field
```typescript
// 1. Add validation
// frontend/src/utils/validators.ts
export const validateNewField = (value: string): string => {
  if (!value) return 'This field is required';
  if (value.length < 3) return 'Must be at least 3 characters';
  return '';
};

// 2. Add to form component
// frontend/src/components/modals/CreateFundEventModal.tsx
const [newField, setNewField] = useState('');
const [newFieldError, setNewFieldError] = useState('');

const handleNewFieldChange = (value: string) => {
  setNewField(value);
  setNewFieldError(validateNewField(value));
};

return (
  <TextField
    fullWidth
    label="New Field"
    value={newField}
    onChange={(e) => handleNewFieldChange(e.target.value)}
    error={!!newFieldError}
    helperText={newFieldError}
    required
  />
);
```

## Testing Guidelines

### 1. Component Testing Checklist
- [ ] Test component renders correctly
- [ ] Test with null/undefined values
- [ ] Test user interactions (clicks, form inputs)
- [ ] Test error states
- [ ] Test loading states
- [ ] Test with different data scenarios

### 2. Test Structure
```typescript
describe('ComponentName', () => {
  // Setup
  const mockProps = {
    // ... mock props
  };

  // Happy path tests
  it('should render correctly', () => {
    render(<Component {...mockProps} />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  // Edge case tests
  it('should handle null values', () => {
    const propsWithNulls = { ...mockProps, someValue: null };
    render(<Component {...propsWithNulls} />);
    // Verify graceful handling
  });

  // Interaction tests
  it('should handle user interactions', () => {
    render(<Component {...mockProps} />);
    fireEvent.click(screen.getByText('Button'));
    // Verify expected behavior
  });
});
```

### 3. Running Tests
```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- NewSection.test.tsx

# Run tests matching pattern
npm test -- --testNamePattern="should render"
```

## Code Review Guidelines

### 1. Review Checklist
- [ ] Component follows established patterns
- [ ] Props interface is consistent
- [ ] Error handling is implemented
- [ ] Loading states are handled
- [ ] Tests are comprehensive
- [ ] Performance considerations addressed
- [ ] No console errors or warnings
- [ ] TypeScript types are correct

### 2. Common Issues to Avoid
```typescript
// ❌ DON'T: Create components without proper interfaces
const MyComponent = (props) => {
  // No TypeScript interface
};

// ✅ DO: Use proper TypeScript interfaces
interface MyComponentProps {
  data: MyDataType;
  onAction: (id: number) => void;
}

const MyComponent: React.FC<MyComponentProps> = ({ data, onAction }) => {
  // Properly typed component
};

// ❌ DON'T: Use inline styles or duplicate logic
const MyComponent = () => {
  return (
    <div style={{ padding: '6px', marginBottom: '8px' }}>
      {/* Inline styles */}
    </div>
  );
};

// ✅ DO: Use Material-UI components and centralized utilities
const MyComponent = () => {
  return (
    <Paper sx={{ p: 0.75, mb: 1, borderRadius: 2 }}>
      {/* Consistent styling */}
    </Paper>
  );
};
```

## Performance Guidelines

### 1. Memoization Patterns
```typescript
// ✅ DO: Memoize expensive calculations
const expensiveData = useMemo(() => {
  return calculateExpensiveData(fund);
}, [fund.current_equity_balance, fund.average_equity_balance]);

// ✅ DO: Memoize event handlers
const handleAction = useCallback((id: number) => {
  onAction(id);
}, [onAction]);

// ❌ DON'T: Recreate objects on every render
const MyComponent = ({ data }) => {
  const processedData = data.map(item => ({ ...item, processed: true })); // Recreated every render
};
```

### 2. Conditional Rendering
```typescript
// ✅ DO: Use conditional rendering for performance
if (!data || data.length === 0) {
  return <NoDataMessage />;
}

// ✅ DO: Only render when necessary
{fund.tracking_type === 'nav_based' && (
  <NavMetricsSection fund={fund} />
)}
```

## Debugging Guide

### 1. Common Debugging Tools
```typescript
// 1. React DevTools
// Install React DevTools browser extension
// Use Components tab to inspect component hierarchy
// Use Profiler tab to identify performance issues

// 2. Console logging
console.log('Component rendered with props:', props);
console.log('State updated:', state);

// 3. Debug utilities
import { debugTableRendering } from '../utils/debug';
debugTableRendering(events, groupedEvents);
```

### 2. Debugging Checklist
- [ ] Check browser console for errors
- [ ] Verify API responses in Network tab
- [ ] Inspect component props in React DevTools
- [ ] Check state updates in React DevTools
- [ ] Verify data flow through components
- [ ] Test with different data scenarios

### 3. Common Issues and Solutions

#### Issue: Component not rendering
```typescript
// Check: Are all required props provided?
// Check: Is there an error in the component?
// Check: Is the component being imported correctly?

// Debug:
console.log('Props received:', props);
console.log('Component state:', state);
```

#### Issue: Data not updating
```typescript
// Check: Is the API call successful?
// Check: Is the state being updated correctly?
// Check: Are dependencies correct in useEffect?

// Debug:
console.log('API response:', response);
console.log('State after update:', state);
```

#### Issue: Performance problems
```typescript
// Check: Are expensive calculations memoized?
// Check: Are event handlers memoized?
// Check: Is conditional rendering used?

// Debug:
console.log('Component render time:', performance.now());
console.log('Expensive calculation result:', expensiveData);
```

## Best Practices Summary

### 1. Component Development
- Keep components under 200 lines
- Use single responsibility principle
- Implement proper error handling
- Add loading states
- Write comprehensive tests

### 2. Code Organization
- Use centralized utilities
- Follow established patterns
- Maintain consistent naming
- Keep related files together

### 3. Performance
- Memoize expensive calculations
- Use conditional rendering
- Optimize re-renders
- Monitor bundle size

### 4. Testing
- Write tests for all components
- Test edge cases and error states
- Maintain 90%+ coverage
- Use meaningful test names

### 5. Code Review
- Follow established patterns
- Ensure proper TypeScript usage
- Check for performance issues
- Verify error handling

## Getting Help

### 1. Documentation Resources
- `docs/COMPONENT_ARCHITECTURE.md` - Component architecture guide
- `docs/TESTING_STANDARDS.md` - Testing guidelines
- `docs/DESIGN_GUIDELINES.md` - Design patterns and conventions

### 2. Code Examples
- Look at existing components for patterns
- Check test files for examples
- Review utility functions for usage

### 3. Team Communication
- Ask questions in team chat
- Request code reviews early
- Share knowledge and patterns
- Document new patterns discovered

This onboarding guide provides the foundation for contributing effectively to the project while maintaining the high standards established during the FundDetail refactoring. 