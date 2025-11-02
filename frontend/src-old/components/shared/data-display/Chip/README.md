# Chip Components

Visual indicators that display concise information with semantic colors.

## Components

### StatusChip
Display status indicators with automatic color mapping.

**When to Use**:
- Fund status (active, completed, suspended)
- Transaction status (pending, processing, success, failed)
- Any status indicator needing semantic colors

**Props**:
```typescript
interface StatusChipProps {
  status: string;           // The status value
  size?: 'small' | 'medium'; // Chip size (default: 'small')
  className?: string;       // Additional CSS classes
}
```

**Color Mapping**:
- **Success** (green): 'active', 'completed', 'success'
- **Warning** (yellow): 'pending', 'processing', 'warning'
- **Error** (red): 'error', 'failed', 'cancelled'
- **Info** (blue): 'info', 'draft', or any other value

**Example**:
```tsx
import { StatusChip } from '@/components/shared/data-display/Chip';

// In component
<StatusChip status="active" />
<StatusChip status="error" size="medium" />
```

---

### EventTypeChip
Display fund event types with color-coded categories.

**When to Use**:
- Fund event type indicators
- Transaction type displays
- Event history tables

**Props**:
```typescript
interface EventTypeChipProps {
  eventType: string;        // The event type
  size?: 'small' | 'medium'; // Chip size (default: 'small')
  className?: string;       // Additional CSS classes
}
```

**Color Mapping**:
Uses `getEventTypeColor` utility to map event types to appropriate colors.

**Example**:
```tsx
import { EventTypeChip } from '@/components/shared/data-display/Chip';

// In component
<EventTypeChip eventType="NAV_UPDATE" />
<EventTypeChip eventType="DISTRIBUTION" size="medium" />
```

---

### TrackingTypeChip
Display fund tracking type (NAV-based vs Cost-based).

**When to Use**:
- Fund summary displays
- Fund list tables
- Anywhere tracking type distinction is needed

**Props**:
```typescript
interface TrackingTypeChipProps {
  trackingType: string;     // 'nav_based' or 'cost_based'
  size?: 'small' | 'medium'; // Chip size (default: 'small')
  className?: string;       // Additional CSS classes
}
```

**Color Mapping**:
- **Primary** (blue): 'nav_based'
- **Success** (green): 'cost_based'
- **Default** (gray): Unknown types

**Example**:
```tsx
import { TrackingTypeChip } from '@/components/shared/data-display/Chip';

// In component
<TrackingTypeChip trackingType="nav_based" />
<TrackingTypeChip trackingType="cost_based" size="medium" />
```

---

## Common Patterns

### In Tables
```tsx
import { StatusChip, EventTypeChip } from '@/components/shared/data-display/Chip';

<TableCell>
  <StatusChip status={fund.status} />
</TableCell>
<TableCell>
  <EventTypeChip eventType={event.event_type} />
</TableCell>
```

### In Cards
```tsx
import { StatusChip, TrackingTypeChip } from '@/components/shared/data-display/Chip';

<Box display="flex" gap={1}>
  <StatusChip status={fund.status} />
  <TrackingTypeChip trackingType={fund.tracking_type} />
</Box>
```

### With Custom Styling
```tsx
<StatusChip 
  status="active" 
  className="custom-chip"
  size="medium"
/>
```

---

## Design Principles

1. **Semantic Colors**: Colors convey meaning automatically
2. **Consistent Sizing**: Use 'small' for tables, 'medium' for cards/headers
3. **Text Transformation**: No uppercase transformation - respects input casing
4. **Theme Integration**: Uses theme palette colors for consistency

---

## Accessibility

- Chips use semantic colors with sufficient contrast
- Status information should also be conveyed through text/icons for color-blind users
- Use `aria-label` if chip meaning isn't clear from context

---

## When NOT to Use

❌ Don't use chips for:
- Clickable actions (use Button instead)
- Long text labels (use Badge or Typography)
- Interactive selections (use Toggle or Checkbox)

✅ Use chips for:
- Read-only status indicators
- Category/type labels
- Visual metadata displays

