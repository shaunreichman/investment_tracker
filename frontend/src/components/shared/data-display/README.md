# Data Display Components

Reusable components for displaying data in consistent, accessible formats.

## Categories

### 📊 [Chip](./Chip/README.md)
Visual indicators for status, event types, and categories.
- `StatusChip` - Status indicators with semantic colors
- `EventTypeChip` - Fund event type displays
- `TrackingTypeChip` - Fund tracking type indicators

### 🎴 Card (Coming in Phase 1)
Data presentation in card formats.
- `StatCard` - Single metric displays
- `DataCard` - Multi-row data displays
- `SummaryCard` - Complex summaries

### 📈 Chart (Coming in Phase 1)
Data visualization components.
- `LineChart` - Time-series line charts
- More chart types coming

### 📋 Table (Coming in Phase 2-4)
Advanced table components with sorting, filtering, pagination.

---

## Usage

```tsx
// Import from category
import { StatusChip } from '@/components/shared/data-display/Chip';

// Or import from top level
import { StatusChip } from '@/components/shared/data-display';

// Use in component
<StatusChip status="active" />
```

---

## Design Principles

1. **Pure Presentation**: No business logic, receive data via props
2. **Composable**: Can be combined with other components
3. **Accessible**: WCAG compliant, keyboard navigable
4. **Theme-Aware**: Use theme colors and spacing
5. **Responsive**: Adapt to different screen sizes

---

## When to Use Shared vs Domain Components

**Use shared/data-display/** when:
- Component is pure presentation
- Has no domain-specific logic
- Can be reused across multiple features
- Represents common data display patterns

**Use domains/*/features/** when:
- Component has domain-specific logic
- Fetches data or manages state
- Contains business rules
- Combines multiple shared components with domain logic

---

## Adding New Components

1. Create subdirectory: `ComponentName/`
2. Add files:
   - `ComponentName.tsx` - Component implementation
   - `ComponentName.types.ts` - TypeScript types
   - `index.ts` - Barrel export
3. Update category `index.ts`
4. Add documentation to category `README.md`
5. Update this file with new component

---

## Quality Standards

All components must:
- ✅ Have TypeScript types exported
- ✅ Have JSDoc comments
- ✅ Have usage examples in README
- ✅ Pass TypeScript compilation
- ✅ Pass ESLint
- ✅ Be accessible (WCAG AA minimum)

