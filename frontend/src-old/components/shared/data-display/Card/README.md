// Card Components

Display data in card formats with consistent styling and flexible layouts.

## Components

### StatCard
Display a single statistic with optional icon, trend, and subtitle.

**When to Use**:
- Dashboard KPIs and metrics
- Summary statistics
- Portfolio totals
- Performance indicators

**Props**:
```typescript
interface StatCardProps {
  title: string;              // Stat label
  value: string | number;     // Main value
  subtitle?: string;          // Additional context
  icon?: ReactNode;           // Icon to display
  color?: 'primary' | 'success' | 'error' | 'warning' | 'info' | 'default';
  trend?: TrendIndicator;     // Optional trend arrow
  onClick?: () => void;       // Makes card interactive
  className?: string;
}

interface TrendIndicator {
  value: number;              // Percentage change
  direction: 'up' | 'down';   // Trend direction
  isPositive?: boolean;       // Whether trend is good
  label?: string;             // Optional trend label
}
```

**Examples**:
```tsx
import { StatCard } from '@/components/shared/data-display/Card';
import { AccountBalance } from '@mui/icons-material';

// Basic stat
<StatCard
  title="Total Committed"
  value="$1,234,567"
  subtitle="Across 12 funds"
  icon={<AccountBalance />}
  color="primary"
/>

// With trend
<StatCard
  title="Portfolio Value"
  value="$2,345,678"
  color="success"
  trend={{
    value: 12.5,
    direction: 'up',
    isPositive: true,
    label: 'vs last month'
  }}
/>

// Interactive
<StatCard
  title="Active Funds"
  value={8}
  color="info"
  onClick={() => navigate('/funds')}
/>
```

---

### DataCard
Display multiple label-value pairs in a structured format.

**When to Use**:
- Fund details displays
- Entity information
- Configuration settings
- Any key-value data

**Props**:
```typescript
interface DataCardProps {
  title?: string;             // Optional card title
  data: DataRow[];            // Array of rows to display
  onItemClick?: (index: number) => void; // Row click handler
  className?: string;
}

interface DataRow {
  label: string;              // Row label
  value: ReactNode;           // Value (can be component)
  icon?: ReactNode;           // Optional icon
  color?: string;             // Value color
  helperText?: string;        // Additional context
  highlighted?: boolean;      // Emphasize this row
}
```

**Examples**:
```tsx
import { DataCard } from '@/components/shared/data-display/Card';
import { StatusChip } from '@/components/shared/data-display/Chip';
import { CalendarToday, AttachMoney } from '@mui/icons-material';

// Basic data card
<DataCard
  title="Fund Details"
  data={[
    { 
      label: 'Start Date', 
      value: '2021-01-15',
      icon: <CalendarToday fontSize="small" />
    },
    { 
      label: 'Status', 
      value: <StatusChip status="active" />
    },
    { 
      label: 'Expected IRR', 
      value: '12.5%',
      color: 'success.main',
      highlighted: true
    },
    {
      label: 'Committed Capital',
      value: '$500,000',
      icon: <AttachMoney fontSize="small" />,
      helperText: 'Initial commitment'
    },
  ]}
/>

// Without title, interactive rows
<DataCard
  data={[
    { label: 'NAV Updates', value: 24 },
    { label: 'Distributions', value: 6 },
    { label: 'Tax Events', value: 3 },
  ]}
  onItemClick={(index) => console.log(`Clicked row ${index}`)}
/>
```

---

### SummaryCard
Display complex summaries with multiple sections.

**When to Use**:
- Performance summaries
- Portfolio overviews
- Multi-section reports
- Detailed breakdowns

**Props**:
```typescript
interface SummaryCardProps {
  title: string;              // Card title
  icon?: ReactNode;           // Title icon
  sections: SummarySection[]; // Array of sections
  footer?: ReactNode;         // Optional footer
  className?: string;
}

interface SummarySection {
  title?: string;             // Section title
  content: ReactNode | SummarySectionRow[]; // Section content
  showDivider?: boolean;      // Show divider after section
}

interface SummarySectionRow {
  label: string;
  value: ReactNode;
  icon?: ReactNode;
  color?: string;
  emphasized?: boolean;
}
```

**Examples**:
```tsx
import { SummaryCard } from '@/components/shared/data-display/Card';
import { TrendingUp } from '@mui/icons-material';

// Multi-section summary
<SummaryCard
  title="Performance Summary"
  icon={<TrendingUp />}
  sections={[
    {
      title: "Returns",
      content: [
        { 
          label: 'Average IRR', 
          value: '12.5%', 
          color: 'success.main',
          emphasized: true
        },
        { label: 'Multiple', value: '2.3x', color: 'success.main' },
      ],
      showDivider: true
    },
    {
      title: "Capital",
      content: [
        { label: 'Total Invested', value: '$1,200,000' },
        { label: 'Total Returned', value: '$2,800,000' },
        { label: 'Unrealized Value', value: '$600,000' },
      ],
      showDivider: true
    },
    {
      title: "Activity",
      content: [
        { label: 'Completed Funds', value: 3 },
        { label: 'Active Funds', value: 8 },
      ]
    }
  ]}
  footer={
    <Typography variant="caption" color="textSecondary">
      Last updated: {new Date().toLocaleDateString()}
    </Typography>
  }
/>

// Custom content in sections
<SummaryCard
  title="Fund Overview"
  sections={[
    {
      content: (
        <Box>
          <Typography variant="body1">
            Custom content can go here
          </Typography>
          <Button>View Details</Button>
        </Box>
      )
    }
  ]}
/>
```

---

## Common Patterns

### Dashboard Grid
```tsx
import { StatCard } from '@/components/shared/data-display/Card';

<Box display="grid" gridTemplateColumns="repeat(3, 1fr)" gap={3}>
  <StatCard title="Total Committed" value="$1.2M" color="primary" />
  <StatCard title="Current Value" value="$2.8M" color="success" />
  <StatCard title="Active Funds" value={8} color="info" />
</Box>
```

### Combined Cards
```tsx
import { StatCard, DataCard } from '@/components/shared/data-display/Card';

<Box display="flex" flexDirection="column" gap={2}>
  {/* Summary stats */}
  <Box display="grid" gridTemplateColumns="repeat(3, 1fr)" gap={2}>
    <StatCard title="Portfolio Value" value="$2.8M" color="success" />
    <StatCard title="Realized Gains" value="$680K" color="primary" />
    <StatCard title="IRR" value="12.5%" color="info" />
  </Box>
  
  {/* Detailed breakdown */}
  <DataCard
    title="Breakdown"
    data={[...]}
  />
</Box>
```

---

## Design Principles

1. **Consistent Spacing**: All cards use MUI's spacing system
2. **Color Semantics**: Colors convey meaning (success = positive, error = negative)
3. **Responsive**: Cards adapt to container width
4. **Interactive**: Optional onClick for navigation
5. **Composable**: Combine with chips, icons, and other components

---

## Accessibility

- Cards maintain proper heading hierarchy
- Color is not the only indicator of meaning
- Interactive cards have hover states and cursor changes
- Proper keyboard navigation support

---

## When NOT to Use

❌ Don't use cards for:
- Long-form content (use Paper or Container)
- Complex forms (use form components)
- Navigation (use navigation components)

✅ Use cards for:
- Summary statistics
- Data displays
- Grouped information
- Dashboard widgets

