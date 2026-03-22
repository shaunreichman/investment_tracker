# Breadcrumbs Component

Enterprise-grade breadcrumb navigation component with full accessibility, React Router integration, and comprehensive feature support.

## Features

- ✅ **Semantic HTML**: Proper `<nav>`, `<ol>` structure with `aria-current="page"` on terminal crumb
- ✅ **React Router Integration**: Native `<Link>` support with `to` prop
- ✅ **Keyboard Activation**: Enter and Space key support
- ✅ **Overflow Handling**: Middle ellipsis strategy with tooltips for truncated labels
- ✅ **Validation**: Console warnings for duplicate IDs/paths, empty arrays, missing handlers
- ✅ **Design Tokens**: Enforces theme spacing, typography, and palette
- ✅ **Custom Rendering**: Optional `renderItem` prop for complete customization
- ✅ **Analytics Ready**: `segmentMeta` prop reserved for future analytics integration
- ✅ **Accessibility First**: Full ARIA support, keyboard navigation, screen reader friendly

## Usage

### Basic Example

```tsx
import { Breadcrumbs } from '@/shared/ui/navigation';
import type { BreadcrumbItem } from '@/shared/ui/navigation';

function MyPage() {
  const items: BreadcrumbItem[] = [
    { id: 'home', label: 'Home', to: '/' },
    { id: 'companies', label: 'Companies', to: '/companies' },
    { id: 'company-123', label: 'Acme Corp', to: '/companies/123' }
  ];

  return <Breadcrumbs items={items} />;
}
```

### With Icons

```tsx
import { Home, Business, Description } from '@mui/icons-material';

const items: BreadcrumbItem[] = [
  { id: 'home', label: 'Home', to: '/', icon: <Home fontSize="small" /> },
  { id: 'companies', label: 'Companies', to: '/companies', icon: <Business fontSize="small" /> },
  { id: 'company-123', label: 'Acme Corp', to: '/companies/123', icon: <Description fontSize="small" /> }
];

<Breadcrumbs items={items} />
```

### With Long Trail (Overflow)

```tsx
// Automatically collapses middle items when maxItems is set
const longTrail: BreadcrumbItem[] = [
  { id: 'home', label: 'Home', to: '/' },
  { id: 'level1', label: 'Level 1', to: '/level1' },
  { id: 'level2', label: 'Level 2', to: '/level1/level2' },
  { id: 'level3', label: 'Level 3', to: '/level1/level2/level3' },
  { id: 'level4', label: 'Level 4', to: '/level1/level2/level3/level4' },
  { id: 'level5', label: 'Level 5', to: '/level1/level2/level3/level4/level5' },
];

<Breadcrumbs items={longTrail} maxItems={4} />
// Renders: Home ... Level 4 Level 5
```

### With onNavigate Fallback (Non-Router Context)

```tsx
const items: BreadcrumbItem[] = [
  { id: 'home', label: 'Home' },
  { id: 'companies', label: 'Companies' },
];

<Breadcrumbs
  items={items}
  onNavigate={(item) => {
    // Custom navigation logic
    console.log('Navigate to:', item.id);
  }}
/>
```

### With Custom Render

```tsx
<Breadcrumbs
  items={items}
  renderItem={({ item, isLast, index }) => (
    <CustomBreadcrumbItem
      item={item}
      isLast={isLast}
      index={index}
    />
  )}
/>
```

### With Disabled Items

```tsx
const items: BreadcrumbItem[] = [
  { id: 'home', label: 'Home', to: '/' },
  { id: 'disabled', label: 'Disabled', to: '/disabled', disabled: true },
  { id: 'active', label: 'Active', to: '/active' },
];

<Breadcrumbs items={items} />
```

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `items` | `BreadcrumbItem[]` | Yes | - | Array of breadcrumb items (each must have `id` and `label`) |
| `LinkComponent` | `ComponentType` | No | `RouterLink` | Custom Link component (defaults to react-router-dom Link) |
| `onNavigate` | `(item: BreadcrumbItem) => void` | No | - | Fallback navigation handler when `to` is not provided |
| `separator` | `React.ReactNode` | No | MUI default | Custom separator between items |
| `maxItems` | `number` | No | - | Maximum items before collapsing (middle ellipsis) |
| `renderItem` | `(props: BreadcrumbItemRenderProps) => React.ReactNode` | No | - | Custom render function for items |
| `ariaLabel` | `string` | No | `"Breadcrumb"` | ARIA label for navigation |
| `density` | `'compact' \| 'comfortable'` | No | `'comfortable'` | Density variant (future use) |
| `showTooltips` | `boolean` | No | `true` | Show tooltips on truncated labels |
| `className` | `string` | No | - | Custom className |

### BreadcrumbItem Interface

```typescript
interface BreadcrumbItem {
  /** Required unique identifier */
  id: string;
  
  /** Required display label */
  label: string;
  
  /** Optional React Router path (preferred) */
  to?: string;
  
  /** Optional icon element */
  icon?: React.ReactNode;
  
  /** Whether the breadcrumb is disabled */
  disabled?: boolean;
  
  /** Analytics metadata (reserved for future use) */
  segmentMeta?: BreadcrumbSegmentMeta;
}
```

## Accessibility

### Semantic Structure

- Wrapped in `<nav aria-label="Breadcrumb">`
- Uses ordered list (`<ol>`) for breadcrumb trail
- Terminal crumb has `aria-current="page"`

### Keyboard Navigation

- **Enter** or **Space**: Activate breadcrumb item
- Standard link/button keyboard behavior
- Focus management: only clickable items in tab order

### Screen Reader Support

- Proper ARIA labels and roles
- `aria-current="page"` on last item
- `aria-disabled` on disabled items
- Tooltips provide full label text for truncated items

## Validation & Warnings

The component emits console warnings for:

- **Empty items array**: No breadcrumbs to render
- **Duplicate IDs**: May cause accessibility issues
- **Duplicate paths**: May cause navigation confusion
- **Missing navigation handlers**: Intermediate crumbs without `to` or `onNavigate`

## Design Tokens

Component enforces design system tokens:

- **Spacing**: Uses `theme.spacing()` for consistent gaps
- **Typography**: Uses `theme.typography.body2` for labels
- **Palette**: 
  - Active links: `theme.palette.primary.main`
  - Hover: `theme.palette.text.hover`
  - Current page: `theme.palette.text.muted`
  - Disabled: `theme.palette.text.disabled`

## Examples in Production

- **TopBar Component**: Route-aware breadcrumbs with dynamic company/fund names
- **Fund Detail Pages**: Hierarchical navigation (Home → Company → Fund)
- **Company Detail Pages**: Company context breadcrumbs

## Related Components

- `TabNavigation` - Horizontal tab navigation
- `MainSidebar` - Primary vertical navigation

## Testing

Component includes comprehensive tests covering:

- ✅ Rendering and semantic HTML
- ✅ React Router Link integration
- ✅ Keyboard navigation
- ✅ Disabled state handling
- ✅ Overflow/collapse behavior
- ✅ Validation warnings
- ✅ Accessibility attributes

Run tests:
```bash
npm test -- Breadcrumbs.test.tsx
```

## Notes

- Component is fully controlled (parent manages items)
- Last item is always non-clickable (current page indicator)
- Middle ellipsis strategy shows first, some middle, and last items
- Tooltips automatically appear on truncated labels when `showTooltips={true}`
- Component wraps MUI `Breadcrumbs` for consistency with design system

## Future Enhancements

- [ ] Density variants (`compact` vs `comfortable`) - currently placeholder
- [ ] Analytics integration using `segmentMeta` prop
- [ ] Custom separator animations
- [ ] Breadcrumb trail persistence/restoration
