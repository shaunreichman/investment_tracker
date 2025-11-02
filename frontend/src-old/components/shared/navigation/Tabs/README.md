# TabNavigation Component

Generic, reusable tab navigation component for use across all domains.

## Features

- ✅ **Full Keyboard Navigation**: Arrow keys (left/right), Home, End
- ✅ **Accessibility**: ARIA roles, labels, keyboard focus management
- ✅ **Responsive Design**: Mobile-friendly layout
- ✅ **Icon Support**: Optional icons for each tab
- ✅ **Disabled State**: Support for disabled tabs
- ✅ **Theme Integration**: Uses application theme colors (Docker-inspired design)

## Usage

### Basic Example

```tsx
import { TabNavigation } from '@/components/shared/navigation/Tabs';

function MyPage() {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'details', label: 'Details' },
    { id: 'settings', label: 'Settings' }
  ];

  return (
    <>
      <TabNavigation
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        ariaLabel="Page navigation tabs"
      />
      
      {/* Tab content */}
      {activeTab === 'overview' && <OverviewContent />}
      {activeTab === 'details' && <DetailsContent />}
      {activeTab === 'settings' && <SettingsContent />}
    </>
  );
}
```

### With Icons

```tsx
import { Home, Settings, Info } from '@mui/icons-material';

const tabs = [
  { id: 'home', label: 'Home', icon: <Home /> },
  { id: 'settings', label: 'Settings', icon: <Settings /> },
  { id: 'about', label: 'About', icon: <Info /> }
];

<TabNavigation
  tabs={tabs}
  activeTab={activeTab}
  onTabChange={setActiveTab}
/>
```

### With Disabled Tabs

```tsx
const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'details', label: 'Details', disabled: true }, // Disabled
  { id: 'settings', label: 'Settings' }
];

<TabNavigation
  tabs={tabs}
  activeTab={activeTab}
  onTabChange={setActiveTab}
/>
```

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `tabs` | `Tab[]` | Yes | - | Array of tab definitions |
| `activeTab` | `string` | Yes | - | ID of the currently active tab |
| `onTabChange` | `(tabId: string) => void` | Yes | - | Callback when tab changes |
| `ariaLabel` | `string` | No | `"Navigation tabs"` | Accessible label for screen readers |

### Tab Interface

```typescript
interface Tab {
  id: string;           // Unique identifier
  label: string;        // Display text
  icon?: React.ReactNode;  // Optional icon
  disabled?: boolean;   // Disabled state
}
```

## Accessibility

- Uses proper ARIA roles (`role="tablist"`, `role="tab"`)
- Supports keyboard navigation:
  - **Arrow Right/Left**: Navigate between tabs
  - **Home**: Jump to first tab
  - **End**: Jump to last tab
- Proper focus management (only active tab is in tab order)
- Descriptive ARIA labels for screen readers

## Styling

Component uses theme integration for consistent styling:
- Docker-inspired color scheme
- Active tab indicated with blue underline
- Hover states for better UX
- Responsive design (stacks vertically on mobile)

## Examples in Production

- Company Detail Page (`/companies/:companyId`) - Overview, Funds, Analysis, Activity, Details tabs
- Fund Detail Page (planned) - Summary, Events, Performance tabs
- Entity Management (planned) - Entity list tabs

## Related Components

- `Breadcrumbs` - For hierarchical navigation
- `MainSidebar` - For primary navigation

## Notes

- Component is fully controlled (parent manages `activeTab` state)
- Mobile responsive behavior is implemented but breakpoint detection is placeholder (TODO)
- Styling is currently hardcoded to Docker theme - may be made configurable in future

