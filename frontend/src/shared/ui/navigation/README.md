# Navigation Components

Reusable navigation components for consistent UI patterns across all domains.

## Available Components

### TabNavigation
Generic tab navigation with full keyboard support and accessibility.

```tsx
import { TabNavigation } from '@/shared/ui/navigation';

<TabNavigation
  tabs={tabs}
  activeTab={activeTab}
  onTabChange={setActiveTab}
/>
```

See [Tabs/README.md](./Tabs/README.md) for detailed documentation.

### Breadcrumbs
Enterprise-grade hierarchical navigation showing user's location in the application.

```tsx
import { Breadcrumbs } from '@/shared/ui/navigation';
import type { BreadcrumbItem } from '@/shared/ui/navigation';

const items: BreadcrumbItem[] = [
  { id: 'home', label: 'Home', to: '/' },
  { id: 'companies', label: 'Companies', to: '/companies' },
  { id: 'company-123', label: 'Acme Corp', to: '/companies/123' }
];

<Breadcrumbs items={items} />
```

See [Breadcrumbs/README.md](./Breadcrumbs/README.md) for detailed documentation.

## Planned Components

### Pagination (Future)
Pagination controls for large datasets.

### Stepper (Future)
Multi-step process indicator (useful for wizards/forms).

## Design Principles

- **Domain-Agnostic**: All components are reusable across funds, companies, entities, etc.
- **Accessibility First**: ARIA support, keyboard navigation, screen reader friendly
- **Theme Integration**: Consistent with application theme and design system
- **Fully Controlled**: Parent components manage state, these are presentational

## Usage Guidelines

1. **Import from shared**: Always import from `@/shared/ui/navigation`
2. **Keep them generic**: Don't add domain-specific logic to these components
3. **Follow patterns**: Use these components consistently across the application
4. **Accessibility**: Don't remove or modify accessibility features

## Related Directories

- `shared/forms/` - Reusable form components
- `shared/data-display/` - Tables, cards, charts
- `shared/feedback/` - Loading, error, success states
- `layout/` - Application layout components

