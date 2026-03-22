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
import { StatCard } from '@/shared/ui/data-display/Card';
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
import { SummaryCard } from '@/shared/ui/data-display/Card';
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
import { StatCard } from '@/shared/ui/data-display/Card';

<Box display="grid" gridTemplateColumns="repeat(3, 1fr)" gap={3}>
  <StatCard title="Total Committed" value="$1.2M" color="primary" />
  <StatCard title="Current Value" value="$2.8M" color="success" />
  <StatCard title="Active Funds" value={8} color="info" />
</Box>
```

### Combined Cards
```tsx
import { StatCard, SummaryCard } from '@/shared/ui/data-display/Card';

<Box display="flex" flexDirection="column" gap={2}>
  {/* Summary stats */}
  <Box display="grid" gridTemplateColumns="repeat(3, 1fr)" gap={2}>
    <StatCard title="Portfolio Value" value="$2.8M" color="success" />
    <StatCard title="Realized Gains" value="$680K" color="primary" />
    <StatCard title="IRR" value="12.5%" color="info" />
  </Box>
  
  {/* Detailed breakdown */}
  <SummaryCard
    title="Breakdown"
    sections={[...]}
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

---

## Note on DataCard

**DataCard has been excluded from migration** as SummaryCard provides equivalent functionality (single-section summary with label-value rows) and eliminates code duplication. StatCard is kept for its unique single-metric/KPI use case with trend indicators.

