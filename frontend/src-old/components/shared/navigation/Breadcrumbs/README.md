# Breadcrumbs Component

Generic, reusable breadcrumb navigation component for displaying hierarchical navigation paths.

## Features

- ✅ **Hierarchical Navigation**: Shows user's location in the app hierarchy
- ✅ **Interactive Links**: All breadcrumbs are clickable except the last (current page)
- ✅ **Icon Support**: Optional icons for each breadcrumb item
- ✅ **Theme Integration**: Uses application theme colors
- ✅ **Accessibility**: Proper ARIA labels and semantic HTML
- ✅ **Customizable**: Optional separator and max items for long trails
- ✅ **Smart Styling**: Last item styled differently (muted, non-clickable)

## Usage

### Basic Example

```tsx
import { Breadcrumbs } from '@/components/shared/navigation/Breadcrumbs';
import { useNavigate } from 'react-router-dom';

function MyPage() {
  const navigate = useNavigate();

  const breadcrumbItems = [
    { label: 'Home', path: '/' },
    { label: 'Companies', path: '/companies' },
    { label: 'Acme Corp', path: '/companies/123' }
  ];

  return (
    <Breadcrumbs
      items={breadcrumbItems}
      onNavigate={(path) => navigate(path)}
    />
  );
}
```

### With Icons

```tsx
import { Home, Business, Description } from '@mui/icons-material';

const breadcrumbItems = [
  { label: 'Home', path: '/', icon: <Home fontSize="small" /> },
  { label: 'Companies', path: '/companies', icon: <Business fontSize="small" /> },
  { label: 'Acme Corp', path: '/companies/123', icon: <Description fontSize="small" /> }
];

<Breadcrumbs
  items={breadcrumbItems}
  onNavigate={(path) => navigate(path)}
/>
```

### With Custom Separator

```tsx
import { NavigateNext, ChevronRight } from '@mui/icons-material';

<Breadcrumbs
  items={breadcrumbItems}
  onNavigate={(path) => navigate(path)}
  separator={<ChevronRight fontSize="small" />}
/>
```

### With Max Items (Collapsing)

```tsx
// For very long breadcrumb trails, limit visible items
<Breadcrumbs
  items={veryLongBreadcrumbList}
  onNavigate={(path) => navigate(path)}
  maxItems={4} // Will show first, last, and collapse middle items
/>
```

### With Route-Aware Hook Pattern

The recommended pattern is to separate breadcrumb **data logic** (route-aware, domain-specific) from **presentation** (generic component):

```tsx
// Custom hook in your page/layout (domain-specific)
const useBreadcrumbData = () => {
  const location = useLocation();
  const params = useParams();
  const { data: company } = useCompany(params.companyId);

  if (location.pathname === '/') {
    return { breadcrumbs: [{ label: 'Home', path: '/' }] };
  }

  if (location.pathname.startsWith('/companies/')) {
    return {
      breadcrumbs: [
        { label: 'Home', path: '/' },
        { label: company?.name || 'Loading...', path: `/companies/${params.companyId}` }
      ]
    };
  }

  return { breadcrumbs: [{ label: 'Home', path: '/' }] };
};

// Usage in component
function TopBar() {
  const navigate = useNavigate();
  const { breadcrumbs } = useBreadcrumbData(); // Domain-specific logic

  return (
    <Breadcrumbs
      items={breadcrumbs}
      onNavigate={(path) => navigate(path)}
    />
  );
}
```

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `items` | `BreadcrumbItem[]` | Yes | - | Array of breadcrumb items to display |
| `onNavigate` | `(path: string) => void` | Yes | - | Callback when breadcrumb is clicked |
| `separator` | `React.ReactNode` | No | MUI default | Custom separator between items |
| `maxItems` | `number` | No | - | Maximum items to display before collapsing |
| `ariaLabel` | `string` | No | `"breadcrumb"` | Accessible label for screen readers |

### BreadcrumbItem Interface

```typescript
interface BreadcrumbItem {
  label: string;           // Display text
  path: string;            // Navigation path
  icon?: React.ReactNode;  // Optional icon
}
```

## Accessibility

- Uses semantic `<nav>` element via MUI Breadcrumbs
- Proper ARIA labels (`aria-label="breadcrumb"` by default)
- Last item is non-interactive (current page)
- Keyboard navigable (standard link behavior)

## Styling

Component integrates with theme:
- Active links use `theme.palette.primary.main` (Docker blue)
- Hover state uses `theme.palette.text.hover`
- Current page uses `theme.palette.text.muted`
- Last item has reduced font weight (400 vs 500)

## Design Decisions

### Separation of Concerns
- **Component**: Pure presentation, domain-agnostic
- **Hook Pattern**: Domain logic lives in consuming code (e.g., `useBreadcrumbData` in TopBar)
- This keeps the component reusable across different contexts

### Last Item Treatment
- Last breadcrumb is styled as "current page" (muted, non-clickable)
- This is a common UX pattern indicating user's current location

### Icon Placement
- Icons appear before labels
- Use `fontSize="small"` for icons to match text height

## Examples in Production

- **TopBar Component**: Uses `useBreadcrumbData` hook to generate route-aware breadcrumbs
  - Home → Company → Fund hierarchy
  - Dynamically fetches company/fund names

## Related Components

- `TabNavigation` - For horizontal tab navigation within a page
- `MainSidebar` - For primary vertical navigation

## Notes

- Component wraps MUI `Breadcrumbs` for consistency with existing design system
- Keep breadcrumb trails shallow (3-5 levels max) for usability
- Use `maxItems` for deep hierarchies to prevent horizontal overflow

