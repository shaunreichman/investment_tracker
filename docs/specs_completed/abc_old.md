# Component Architecture Refactor Specification

**Status:** Planning  
**Created:** 2025-01-12  
**Author:** AI Assistant  
**Version:** 1.0  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Target Architecture](#target-architecture)
4. [Component Patterns](#component-patterns)
5. [Directory Structure](#directory-structure)
6. [Migration Strategy](#migration-strategy)
7. [Implementation Phases](#implementation-phases)
8. [Testing Strategy](#testing-strategy)
9. [Success Criteria](#success-criteria)
10. [Appendices](#appendices)

---

## Executive Summary

### Purpose
Refactor the frontend component architecture to create a maintainable, scalable, and enterprise-grade component structure that follows React best practices and integrates seamlessly with the newly refactored hooks system.

### Goals
1. ✅ **Reduce complexity** - Split large monolithic components into smaller, focused pieces
2. ✅ **Establish patterns** - Clear separation between smart (container) and dumb (presentational) components
3. ✅ **Improve testability** - Isolated, single-responsibility components
4. ✅ **Integrate new hooks** - Replace all old hooks with new refactored hooks
5. ✅ **Enhance reusability** - Extract common UI patterns into reusable components
6. ✅ **Better organization** - Logical grouping by domain and responsibility

### Key Metrics
- **Current:** 79 component files, average 200 lines per file, 8+ useState per page component
- **Target:** ~85 component files, average 120 lines per file, 3-4 useState per page component
- **Impact:** 40% reduction in component complexity, 100% hook migration

### Timeline
- **Phase 1 (Forms):** 3-4 days
- **Phase 2 (Lists):** 2-3 days
- **Phase 3 (Pages):** 4-5 days
- **Phase 4 (Cleanup):** 1-2 days
- **Total:** 10-14 days

---

## Current State Analysis

### Component Inventory

#### By Category
```
Current: 79 TSX files
├── Domain Components (51 files - 64%)
│   ├── companies/ (24 files)
│   ├── fund/ (18 files)
│   └── entities/ (9 files)
│
├── UI Components (14 files - 18%)
│   ├── ui/ (9 files)
│   └── forms/ (5 files)
│
├── Layout Components (3 files - 4%)
│
├── Top-Level Modals (3 files - 4%)
│
└── Other (8 files - 10%)
```

#### By Size (Lines of Code)
```
Distribution:
├── 0-100 lines:   32 files (41%) ✅ Good size
├── 101-200 lines: 28 files (35%) ✅ Acceptable
├── 201-300 lines: 12 files (15%) ⚠️ Large
├── 301-400 lines:  4 files (5%)  🚩 Very large
└── 400+ lines:     3 files (4%)  🚩 Refactor needed
```

**Problematic Files:**
- `CompaniesPage.tsx` - 485 lines
- `FundDetail.tsx` - 447 lines
- `ErrorDisplay.tsx` - 443 lines
- `CreateFundModal.tsx` - 404 lines

### Current Issues

#### 1. Large Monolithic Components
**Problem:** Single components handling multiple concerns

**Example: CompaniesPage.tsx (485 lines)**
```typescript
// PROBLEMS:
// - 8+ useState declarations
// - 3 different data fetching hooks (old)
// - 10+ event handlers
// - Tab management logic
// - Modal management
// - Error handling
// - UI rendering
```

**Impact:**
- ❌ Hard to understand
- ❌ Difficult to test
- ❌ Impossible to reuse parts
- ❌ High change risk

#### 2. Old Hooks Usage
**Problem:** Components still use deprecated hooks

**Current Old Hook Usage:**
```typescript
// Found in 12+ components:
useCompaniesold()
useFundsold()
useEntitiesold()
useUnifiedFormold()
useDebouncedSearch()
useResponsiveView()
useTableSorting()
useFundsFilters()
```

**Impact:**
- ❌ Not using new validated schemas
- ❌ Not using transformers
- ❌ Inconsistent patterns
- ❌ Technical debt

#### 3. Inconsistent Patterns
**Problem:** Mixed approaches to similar problems

**Examples:**
```typescript
// Some components fetch data:
const CompanyDetails = () => {
  const { data } = useCompanyDetails();
  // ...
};

// Others receive data:
const CompanyDetails = ({ data }: Props) => {
  // ...
};

// Some use local state:
const [viewMode, setViewMode] = useState('table');

// Others use custom hooks:
const { viewMode, handleViewModeChange } = useResponsiveView();

// Some use Material-UI directly:
<TextField onChange={handleChange} />

// Others use wrapper components:
<FormTextField onChange={handleChange} />
```

**Impact:**
- ❌ Confusing for developers
- ❌ Hard to maintain
- ❌ Difficult to establish standards

#### 4. Prop Drilling
**Problem:** Props passed through multiple levels

**Example:**
```typescript
// CompaniesPage.tsx
<FundsTab 
  onDeleteFund={handleDeleteFund}
  refetchFunds={refetchFunds}
/>

// FundsTab.tsx
<FundsTable 
  onDeleteFund={onDeleteFund}
  refetch={refetchFunds}
/>

// FundsTable.tsx
<FundRow 
  onDelete={onDeleteFund}
/>

// FundRow.tsx (finally used!)
<Button onClick={() => onDelete(fund)} />
```

**Impact:**
- ❌ Tight coupling
- ❌ Verbose code
- ❌ Hard to refactor

#### 5. Tab-Based Organization
**Problem:** Tabs organized by UI structure, not by responsibility

**Current:**
```
companies/
├── overview-tab/
├── funds-tab/
├── activity-tab/
├── analysis-tab/
└── company-details-tab/
```

**Issues:**
- ❌ Tabs not reusable outside CompaniesPage
- ❌ Tab components receive all data as props
- ❌ Can't test tabs in isolation
- ❌ Organization reflects UI, not domain

---

## Target Architecture

### Architectural Principles

#### 1. Smart vs Dumb Components
**Smart Components (Containers)**
- Fetch data using hooks
- Manage state
- Handle business logic
- Orchestrate dumb components
- Located in: `pages/` and `features/`

**Dumb Components (Presentational)**
- Receive data via props
- No hooks (except UI-only like `useState` for local toggles)
- Pure rendering logic
- Highly reusable
- Located in: `ui/`

#### 2. Component Hierarchy
```
Level 1: Pages         (Route-level, orchestration)
    ↓
Level 2: Features      (Domain logic, data fetching)
    ↓
Level 3: UI Components (Presentation, reusable)
```

#### 3. Data Flow
```
Pages
  └→ Manage route state (URL params, active tab)
  └→ Minimal/no data fetching
  
Features
  └→ Fetch domain-specific data
  └→ Manage local state (filters, sorting)
  └→ Handle user actions
  
UI Components
  └→ Receive data as props
  └→ Call callbacks for events
  └→ No side effects
```

#### 4. State Management Strategy

**Local State (useState/useReducer)**
```typescript
// Use for:
// - UI-only state (modals, accordions, sorting)
// - Form input values (managed by useForm)
// - Temporary state

const modal = useToggle();
const [sortBy, setSortBy] = useState('date');
const [expanded, setExpanded] = useState(false);
```

**URL State (useSearchParams)**
```typescript
// Use for:
// - Active tab
// - Filter/search parameters
// - Pagination
// - Any shareable/bookmarkable state

const [searchParams, setSearchParams] = useSearchParams();
const activeTab = searchParams.get('tab') || 'overview';
```

**Server State (React Query via data hooks)**
```typescript
// Use for:
// - Data from API
// - Cached automatically
// - Managed by domain-specific hooks from hooks/data/

import { useFunds, useDeleteFund } from '@/hooks/data/funds';

const { data: funds, loading, error, refetch } = useFunds({
  filters: { company_id: companyId },
  sort: { field: 'start_date', order: 'desc' }
});

const { mutate: deleteFund, loading: deleting } = useDeleteFund({
  onSuccess: () => refetch()
});
```

**Global State (Zustand) - Minimal**
```typescript
// Use ONLY for:
// - Sidebar visibility (persists across navigation)
// - User authentication
// - Theme preferences
// - True cross-component global UI state

import { useSidebarState } from '@/store';

const { isVisible, toggle } = useSidebarState('fundDetail');

// MIGRATE AWAY: Table filters, sorting → URL params or local state
// KEEP: Sidebar visibility, theme, auth state
```

### Component Responsibilities Matrix

| Component Type | Data Fetching | State Management | Business Logic | UI Rendering | Location |
|---------------|---------------|------------------|----------------|--------------|----------|
| **Pages** | Minimal (metadata only) | Route state (tabs, modals) | Orchestration only | Layout + features | `pages/` |
| **Features** | Yes (domain data) | Local state (filters, sorting) | Yes (domain logic) | Compose UI components | `features/` |
| **UI Components** | No | UI-only state (expansion) | No | Pure presentation | `ui/` |
| **Layout** | No | No | No | Structure only | `layout/` |

---

## Component Patterns

### Pattern 1: Page Component

**Purpose:** Route-level orchestration, minimal logic

**Template:**
```typescript
// pages/CompaniesPage/CompaniesPage.tsx

import React, { useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { Box, Typography, Button } from '@mui/material';

// Feature imports
import { CompanyOverview } from '@/components/features/company/CompanyOverview';
import { CompanyFundsList } from '@/components/features/company/CompanyFundsList';
import { CompanyDetails } from '@/components/features/company/CompanyDetails';

// UI imports
import { TabNavigation } from '@/components/ui/TabNavigation';
import { PageLayout } from '@/components/layout/PageLayout';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

// Hook imports
import { useToggle } from '@/hooks/ui';
import { useCompany } from '@/hooks/data/companies';

/**
 * Companies Page - Route component
 * 
 * Responsibilities:
 * - URL parameter management
 * - Tab navigation state
 * - Layout orchestration
 * - Feature component rendering
 * 
 * Does NOT:
 * - Fetch domain data (features do this)
 * - Implement business logic (features do this)
 * - Render complex UI (features/UI components do this)
 */
export const CompaniesPage = () => {
  // Route params
  const { companyId } = useParams<{ companyId: string }>();
  
  // URL state for tabs
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'overview';
  
  // Modal state
  const createModal = useToggle();
  
  // Minimal data fetching (just metadata for page header)
  const { data: company, loading } = useCompany(parseInt(companyId || '0'));
  
  // Tab configuration
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'funds', label: 'Funds' },
    { id: 'details', label: 'Details' },
  ];
  
  // Tab change handler
  const handleTabChange = (tabId: string) => {
    setSearchParams({ tab: tabId });
  };
  
  // Loading state
  if (loading) {
    return <LoadingSpinner label="Loading company..." />;
  }
  
  // Error state
  if (!company) {
    return <ErrorDisplay message="Company not found" />;
  }
  
  return (
    <PageLayout>
      {/* Page Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h3">{company.name}</Typography>
        <Button onClick={createModal.setTrue}>Create Fund</Button>
      </Box>
      
      {/* Tab Navigation */}
      <TabNavigation 
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={handleTabChange}
      />
      
      {/* Tab Content - Feature Components */}
      <Box sx={{ mt: 3 }}>
        {activeTab === 'overview' && (
          <CompanyOverview companyId={company.id} />
        )}
        
        {activeTab === 'funds' && (
          <CompanyFundsList companyId={company.id} />
        )}
        
        {activeTab === 'details' && (
          <CompanyDetails companyId={company.id} />
        )}
      </Box>
      
      {/* Modals */}
      {createModal.value && (
        <CreateFundModal 
          companyId={company.id}
          open={createModal.value}
          onClose={createModal.setFalse}
        />
      )}
    </PageLayout>
  );
};
```

**Key Characteristics:**
- ✅ 80-150 lines typical
- ✅ 2-4 useState declarations
- ✅ Minimal data fetching
- ✅ Simple orchestration logic
- ✅ Delegates complexity to features

---

### Pattern 2: Feature Component

**Purpose:** Domain-specific logic and data management

**Template:**
```typescript
// features/company/CompanyFundsList/CompanyFundsList.tsx

import React, { useState } from 'react';
import { Box, Card } from '@mui/material';

// Presentational components
import { FundsTable } from './components/FundsTable';
import { FundsCards } from './components/FundsCards';
import { FundsFilters } from './components/FundsFilters';

// UI components
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { EmptyState } from '@/components/ui/EmptyState';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';

// Hooks
import { useFunds, useDeleteFund } from '@/hooks/data/funds';
import { useToggle } from '@/hooks/ui';
import { useErrorHandler } from '@/hooks/core/error';

// Types
import type { Fund } from '@/types/models/fund';
import type { CompanyFundsListProps } from './CompanyFundsList.types';

/**
 * Company Funds List - Feature component
 * 
 * Responsibilities:
 * - Fetch funds data for a company
 * - Manage local state (filters, view mode, sorting)
 * - Handle user actions (delete, edit)
 * - Compose presentational components
 * 
 * Does NOT:
 * - Manage route state (parent's job)
 * - Render generic UI (delegates to components)
 */
export const CompanyFundsList = ({ companyId }: CompanyFundsListProps) => {
  // UI state (local component state)
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table');
  const [sortBy, setSortBy] = useState<string>('start_date');
  const [filters, setFilters] = useState({
    status: 'all',
    currency: 'all',
    search: ''
  });
  
  // Modal state (using refactored UI hook)
  const deleteModal = useToggle();
  const [selectedFund, setSelectedFund] = useState<Fund | null>(null);
  
  // Error handling (centralized pattern)
  const handleError = useErrorHandler();
  
  // Data fetching with refactored hooks
  const { data: funds, loading, error, refetch } = useFunds({
    filters: {
      company_id: companyId,
      ...(filters.status !== 'all' && { status: filters.status }),
      ...(filters.currency !== 'all' && { currency: filters.currency }),
      ...(filters.search && { name: filters.search })
    },
    sort: {
      field: sortBy,
      order: 'desc'
    }
  });
  
  // Mutations with refactored hooks
  const { mutate: deleteFund, loading: deleting } = useDeleteFund({
    onSuccess: () => {
      refetch();
      deleteModal.setFalse();
      setSelectedFund(null);
    }
  });
  
  // Event handlers
  const handleDeleteRequest = (fund: Fund) => {
    setSelectedFund(fund);
    deleteModal.setTrue();
  };
  
  const handleDeleteConfirm = async () => {
    if (selectedFund) {
      await deleteFund(selectedFund.id);
    }
  };
  
  const handleFilterChange = (newFilters: Partial<typeof filters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };
  
  // Loading state
  if (loading) {
    return <LoadingSpinner label="Loading funds..." />;
  }
  
  // Error state (using centralized error handler)
  if (error) {
    handleError(error);
    return <ErrorDisplay error={error} onRetry={refetch} />;
  }
  
  // Empty state
  if (!funds || funds.length === 0) {
    return (
      <EmptyState 
        title="No Funds Found"
        message={
          filters.search || filters.status !== 'all'
            ? 'Try adjusting your filters.'
            : 'This company has no funds yet.'
        }
      />
    );
  }
  
  return (
    <Box>
      {/* Filters */}
      <FundsFilters
        filters={filters}
        viewMode={viewMode}
        onFiltersChange={handleFilterChange}
        onViewModeChange={setViewMode}
      />
      
      {/* Funds Display */}
      <Card>
        {viewMode === 'table' ? (
          <FundsTable
            funds={funds}
            sortBy={sortBy}
            onSortChange={setSortBy}
            onDelete={handleDeleteRequest}
          />
        ) : (
          <FundsCards
            funds={funds}
            onDelete={handleDeleteRequest}
          />
        )}
      </Card>
      
      {/* Delete Confirmation Dialog */}
      {deleteModal.value && selectedFund && (
        <ConfirmDialog
          open={deleteModal.value}
          title="Delete Fund"
          description={`Are you sure you want to delete "${selectedFund.name}"?`}
          confirmLabel="Delete"
          loading={deleting}
          onConfirm={handleDeleteConfirm}
          onCancel={deleteModal.setFalse}
        />
      )}
    </Box>
  );
};
```

**Key Characteristics:**
- ✅ 100-200 lines typical
- ✅ 3-5 useState declarations
- ✅ Uses domain-specific hooks
- ✅ Handles business logic
- ✅ Composes UI components

---

### Pattern 3: Presentational Component

**Purpose:** Pure UI rendering, highly reusable

**Template:**
```typescript
// features/company/CompanyFundsList/components/FundsTable.tsx

import React from 'react';
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  IconButton
} from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';

// Types (explicit type imports)
import type { Fund } from '@/types/models/fund';

/**
 * Funds Table - Presentational component
 * 
 * Responsibilities:
 * - Render table UI
 * - Handle UI-only interactions (row expansion, etc.)
 * - Call callbacks for user actions
 * 
 * Does NOT:
 * - Fetch data
 * - Manage business state
 * - Implement business logic
 */

// Explicit interface with proper TypeScript conventions
interface FundsTableProps {
  readonly funds: Fund[];
  readonly sortBy: string;
  onSortChange: (field: string) => void;
  onDelete: (fund: Fund) => void;
}

export const FundsTable: React.FC<FundsTableProps> = ({ 
  funds, 
  sortBy, 
  onSortChange, 
  onDelete 
}) => {
  // Only UI-only state allowed here
  const [expandedRows, setExpandedRows] = React.useState<Set<number>>(new Set());
  
  const toggleRow = (fundId: number) => {
    setExpandedRows(prev => {
      const next = new Set(prev);
      if (next.has(fundId)) {
        next.delete(fundId);
      } else {
        next.add(fundId);
      }
      return next;
    });
  };
  
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell onClick={() => onSortChange('name')}>
            Name {sortBy === 'name' && '↓'}
          </TableCell>
          <TableCell onClick={() => onSortChange('start_date')}>
            Start Date {sortBy === 'start_date' && '↓'}
          </TableCell>
          <TableCell>Status</TableCell>
          <TableCell>Currency</TableCell>
          <TableCell>Actions</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {funds.map(fund => (
          <TableRow key={fund.id}>
            <TableCell>{fund.name}</TableCell>
            <TableCell>{fund.start_date}</TableCell>
            <TableCell>{fund.status}</TableCell>
            <TableCell>{fund.currency}</TableCell>
            <TableCell>
              <IconButton 
                onClick={() => onDelete(fund)}
                size="small"
                aria-label="Delete fund"
              >
                <DeleteIcon />
              </IconButton>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};
```

**Key Characteristics:**
- ✅ 50-150 lines typical
- ✅ 0-2 useState (UI-only state)
- ✅ No data fetching
- ✅ No business logic
- ✅ Pure props → render

---

### Pattern 4: Form Component

**Purpose:** Form submission with validation

**Template:**
```typescript
// features/fund/CreateFundForm/CreateFundForm.tsx

import React from 'react';
import { Box, Button } from '@mui/material';

// Form components
import { FormTextField } from '@/components/ui/Form/FormTextField';
import { FormSelectField } from '@/components/ui/Form/FormSelectField';
import { FormNumberField } from '@/components/ui/Form/FormNumberField';

// Hooks
import { useForm } from '@/hooks/forms/useForm';
import { useCreateFund } from '@/hooks/data/funds';

// Schemas and transformers (from refactored hooks)
import { createFundSchema } from '@/hooks/forms/schemas/fundSchemas';
import { transformCreateFundForm } from '@/hooks/forms/transformers/fundTransformers';

// Types (explicit type imports for better tree-shaking)
import type { CreateFundFormData } from '@/hooks/forms/schemas/fundSchemas';
import type { Fund } from '@/types/models/fund';

/**
 * Create Fund Form - Feature component
 * 
 * Responsibilities:
 * - Form state management (via useForm)
 * - Client-side validation (via schema)
 * - Form submission
 * - Success/error handling
 * 
 * Does NOT:
 * - Implement validation logic (in schema)
 * - Transform data manually (uses transformer)
 * - Manage modal state (parent's job)
 */

// Explicit interface with proper TypeScript conventions
interface CreateFundFormProps {
  readonly companyId: number;
  onSuccess: (fund: Fund) => void;
  onCancel: () => void;
}

export const CreateFundForm: React.FC<CreateFundFormProps> = ({ 
  companyId, 
  onSuccess, 
  onCancel 
}) => {
  // Form management (using refactored form hook with Zod schema)
  const form = useForm<CreateFundFormData>({
    schema: createFundSchema,
    defaultValues: {
      company_id: companyId,
      currency: 'AUD',
      tracking_type: 'NAV_BASED'
    }
  });
  
  // Mutation (from refactored data hooks)
  const { mutate: createFund, loading } = useCreateFund({
    onSuccess: (fund: Fund) => {
      onSuccess(fund);
      form.reset();
    }
  });
  
  // Submit handler (integrates validation + transformation)
  const onSubmit = form.handleSubmit(async (data: CreateFundFormData) => {
    // Transform using standardized transformer from hooks/forms/transformers
    const payload = transformCreateFundForm(data);
    await createFund(payload);
  });
  
  return (
    <Box component="form" onSubmit={onSubmit}>
      {/* Form Fields */}
      <FormTextField
        {...form.register('name')}
        label="Fund Name"
        required
        error={form.formState.errors.name?.message}
      />
      
      <FormSelectField
        {...form.register('tracking_type')}
        label="Tracking Type"
        required
        options={[
          { value: 'NAV_BASED', label: 'NAV Based' },
          { value: 'COST_BASED', label: 'Cost Based' }
        ]}
        error={form.formState.errors.tracking_type?.message}
      />
      
      <FormSelectField
        {...form.register('currency')}
        label="Currency"
        required
        options={currencyOptions}
        error={form.formState.errors.currency?.message}
      />
      
      <FormNumberField
        {...form.register('commitment_amount')}
        label="Commitment Amount"
        error={form.formState.errors.commitment_amount?.message}
      />
      
      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
        <Button 
          type="submit" 
          variant="contained"
          disabled={loading || !form.formState.isValid}
        >
          {loading ? 'Creating...' : 'Create Fund'}
        </Button>
        <Button 
          type="button"
          variant="outlined"
          onClick={onCancel}
        >
          Cancel
        </Button>
      </Box>
    </Box>
  );
};
```

**Key Characteristics:**
- ✅ Uses `useForm` hook
- ✅ Uses schemas from `hooks/forms/schemas`
- ✅ Uses transformers from `hooks/forms/transformers`
- ✅ Uses mutation hooks from `hooks/data`
- ✅ No manual validation
- ✅ No manual transformation

---

## Directory Structure

### Complete Structure

```
frontend/src/components/
│
├── pages/                              # Route-level components (Smart)
│   ├── CompaniesPage/
│   │   ├── CompaniesPage.tsx           # Page component
│   │   ├── CompaniesPage.types.ts      # Page-specific types
│   │   ├── CompaniesPage.test.tsx      # Page tests
│   │   └── index.ts                    # Barrel export
│   │
│   ├── FundDetailPage/
│   │   ├── FundDetailPage.tsx
│   │   ├── FundDetailPage.types.ts
│   │   ├── FundDetailPage.test.tsx
│   │   └── index.ts
│   │
│   ├── EntitiesPage/
│   │   ├── EntitiesPage.tsx
│   │   ├── EntitiesPage.types.ts
│   │   ├── EntitiesPage.test.tsx
│   │   └── index.ts
│   │
│   ├── DashboardPage/
│   │   ├── DashboardPage.tsx
│   │   ├── DashboardPage.types.ts
│   │   ├── DashboardPage.test.tsx
│   │   └── index.ts
│   │
│   └── index.ts                        # Export all pages
│
├── features/                           # Domain-specific features (Smart)
│   ├── company/
│   │   ├── CompanyOverview/
│   │   │   ├── CompanyOverview.tsx     # Feature component
│   │   │   ├── components/             # Feature-specific presentational
│   │   │   │   ├── QuickStatsGrid.tsx
│   │   │   │   ├── PortfolioSummaryCards.tsx
│   │   │   │   └── PerformanceSummary.tsx
│   │   │   ├── CompanyOverview.types.ts
│   │   │   ├── CompanyOverview.test.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── CompanyFundsList/
│   │   │   ├── CompanyFundsList.tsx
│   │   │   ├── components/
│   │   │   │   ├── FundsTable.tsx
│   │   │   │   ├── FundsCards.tsx
│   │   │   │   ├── FundsFilters.tsx
│   │   │   │   └── FundRow.tsx
│   │   │   ├── CompanyFundsList.types.ts
│   │   │   ├── CompanyFundsList.test.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── CompanyDetails/
│   │   │   ├── CompanyDetails.tsx
│   │   │   ├── components/
│   │   │   │   ├── CompanyInfo.tsx
│   │   │   │   ├── ContactInfo.tsx
│   │   │   │   └── BusinessDetails.tsx
│   │   │   ├── CompanyDetails.types.ts
│   │   │   ├── CompanyDetails.test.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── CompanyActivity/
│   │   │   ├── CompanyActivity.tsx
│   │   │   ├── CompanyActivity.types.ts
│   │   │   ├── CompanyActivity.test.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── CompanyAnalysis/
│   │   │   ├── CompanyAnalysis.tsx
│   │   │   ├── CompanyAnalysis.types.ts
│   │   │   ├── CompanyAnalysis.test.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── CreateCompanyForm/
│   │   │   ├── CreateCompanyForm.tsx
│   │   │   ├── CreateCompanyForm.types.ts
│   │   │   ├── CreateCompanyForm.test.tsx
│   │   │   └── index.ts
│   │   │
│   │   └── index.ts                    # Export all company features
│   │
│   ├── fund/
│   │   ├── FundSummary/
│   │   │   ├── FundSummary.tsx
│   │   │   ├── components/
│   │   │   │   ├── EquitySection.tsx
│   │   │   │   ├── PerformanceSection.tsx
│   │   │   │   ├── FundDetailsSection.tsx
│   │   │   │   └── TransactionSummary.tsx
│   │   │   ├── FundSummary.types.ts
│   │   │   ├── FundSummary.test.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── FundEventsList/
│   │   │   ├── FundEventsList.tsx
│   │   │   ├── components/
│   │   │   │   ├── EventsTable.tsx
│   │   │   │   ├── EventRow.tsx
│   │   │   │   ├── GroupedEventRow.tsx
│   │   │   │   └── EventsFilters.tsx
│   │   │   ├── FundEventsList.types.ts
│   │   │   ├── FundEventsList.test.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── CreateFundForm/
│   │   │   ├── CreateFundForm.tsx
│   │   │   ├── CreateFundForm.types.ts
│   │   │   ├── CreateFundForm.test.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── CreateFundEventForm/
│   │   │   ├── CreateFundEventForm.tsx
│   │   │   ├── components/
│   │   │   │   ├── EventTypeSelector.tsx
│   │   │   │   ├── NavUpdateFields.tsx
│   │   │   │   ├── DistributionFields.tsx
│   │   │   │   ├── UnitTransactionFields.tsx
│   │   │   │   └── TaxStatementFields.tsx
│   │   │   ├── CreateFundEventForm.types.ts
│   │   │   ├── CreateFundEventForm.test.tsx
│   │   │   └── index.ts
│   │   │
│   │   └── index.ts                    # Export all fund features
│   │
│   ├── entity/
│   │   ├── EntityList/
│   │   │   ├── EntityList.tsx
│   │   │   ├── components/
│   │   │   │   ├── EntityTable.tsx
│   │   │   │   ├── EntityCards.tsx
│   │   │   │   └── EntityFilters.tsx
│   │   │   ├── EntityList.types.ts
│   │   │   ├── EntityList.test.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── CreateEntityForm/
│   │   │   ├── CreateEntityForm.tsx
│   │   │   ├── CreateEntityForm.types.ts
│   │   │   ├── CreateEntityForm.test.tsx
│   │   │   └── index.ts
│   │   │
│   │   └── index.ts                    # Export all entity features
│   │
│   └── index.ts                        # Export all features
│
├── ui/                                 # Generic presentational components (Dumb)
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.types.ts
│   │   ├── Button.test.tsx
│   │   └── index.ts
│   │
│   ├── Card/
│   │   ├── Card.tsx
│   │   ├── Card.types.ts
│   │   ├── Card.test.tsx
│   │   └── index.ts
│   │
│   ├── Table/
│   │   ├── Table.tsx
│   │   ├── TableHead.tsx
│   │   ├── TableBody.tsx
│   │   ├── TableRow.tsx
│   │   ├── Table.types.ts
│   │   ├── Table.test.tsx
│   │   └── index.ts
│   │
│   ├── Form/
│   │   ├── FormField.tsx               # Base field wrapper
│   │   ├── FormTextField.tsx           # Text input
│   │   ├── FormNumberField.tsx         # Number input
│   │   ├── FormDateField.tsx           # Date picker
│   │   ├── FormSelectField.tsx         # Select dropdown
│   │   ├── FormCheckboxField.tsx       # Checkbox
│   │   ├── Form.types.ts
│   │   ├── Form.test.tsx
│   │   └── index.ts
│   │
│   ├── Modal/
│   │   ├── Modal.tsx
│   │   ├── ConfirmDialog.tsx
│   │   ├── Modal.types.ts
│   │   ├── Modal.test.tsx
│   │   └── index.ts
│   │
│   ├── Feedback/
│   │   ├── LoadingSpinner.tsx
│   │   ├── ErrorDisplay.tsx
│   │   ├── ErrorBoundary.tsx
│   │   ├── SuccessBanner.tsx
│   │   ├── EmptyState.tsx
│   │   ├── Feedback.types.ts
│   │   ├── Feedback.test.tsx
│   │   └── index.ts
│   │
│   ├── Chips/
│   │   ├── StatusChip.tsx
│   │   ├── TrackingTypeChip.tsx
│   │   ├── EventTypeChip.tsx
│   │   ├── Chips.types.ts
│   │   ├── Chips.test.tsx
│   │   └── index.ts
│   │
│   ├── Navigation/
│   │   ├── TabNavigation.tsx
│   │   ├── Breadcrumbs.tsx
│   │   ├── Navigation.types.ts
│   │   ├── Navigation.test.tsx
│   │   └── index.ts
│   │
│   └── index.ts                        # Export all UI components
│
├── layout/                             # Layout components
│   ├── RouteLayout.tsx                 # Main app layout
│   ├── MainSidebar.tsx                 # Sidebar navigation
│   ├── TopBar.tsx                      # Top navigation bar
│   ├── PageLayout.tsx                  # Standard page wrapper
│   ├── layout.types.ts
│   ├── layout.test.tsx
│   └── index.ts
│
└── index.ts                            # Export all components
```

### Naming Conventions

#### Component Files
```
✅ GOOD:
CompanyFundsList.tsx          # PascalCase, descriptive
CreateFundForm.tsx            # PascalCase, action + domain
FundsTable.tsx                # PascalCase, component type

❌ BAD:
company-funds-list.tsx        # kebab-case (wrong)
companyFundsList.tsx          # camelCase (wrong)
FundsTab.tsx                  # "Tab" is UI structure, not responsibility
```

#### Directory Names
```
✅ GOOD:
CompanyFundsList/             # Matches component name
CreateFundForm/               # Matches component name
components/                   # Generic folder for sub-components

❌ BAD:
company-funds-list/           # kebab-case (wrong)
funds-tab/                    # UI structure name (wrong)
sub-components/               # Verbose (wrong)
```

#### Type Files
```
✅ GOOD:
CompanyFundsList.types.ts     # Matches component name
CreateFundForm.types.ts       # Matches component name

❌ BAD:
types.ts                      # Too generic
CompanyFundsList.d.ts         # .d.ts for declaration files only
```

---

## Migration Strategy

### Migration Principles

1. **Incremental, Not Big Bang**
   - Migrate one domain at a time
   - Keep old and new structures working side-by-side
   - Update imports progressively
   
2. **Forms First (Highest Value)**
   - Immediate benefit from new hooks
   - Clear scope
   - Easy to verify
   
3. **Test Before Delete**
   - Verify all imports updated
   - Test functionality
   - Then delete old files
   
4. **Document As You Go**
   - Update import paths in README
   - Add migration notes
   - Track completed migrations

### Migration Phases

#### Phase 1: Update Forms (3-4 days)
**Goal:** Replace all old form hooks with new form system

**Scope:**
- CreateFundModal → CreateFundForm
- CreateCompanyModal → CreateCompanyForm
- CreateEntityModal → CreateEntityForm
- CreateFundEventModal → CreateFundEventForm
- All event form components

**Process for Each Form:**
```
1. Identify current form
2. Find corresponding schema in hooks/forms/schemas
3. Find corresponding transformer in hooks/forms/transformers
4. Replace useUnifiedFormold with useForm
5. Update field components to use ui/Form components
6. Update submission logic to use transformer
7. Test form validation and submission
8. Update imports in parent components
9. Delete old form component
```

#### Phase 2: Update List Components (2-3 days)
**Goal:** Remove old UI hooks, use proper patterns

**Scope:**
- FundsTab.tsx
- CompanyList.tsx
- EntityList.tsx

**Process for Each List:**
```
1. Remove useDebouncedSearch → use direct state + useDebounce (if created)
2. Remove useResponsiveView → use simple useState
3. Remove useTableSorting → use URL params or local state
4. Remove useFundsFilters → use local state
5. Update data fetching to use new hooks
6. Test filtering, sorting, searching
7. Update imports
```

#### Phase 3: Split Large Page Components (4-5 days)
**Goal:** Break monoliths into pages + features

**Scope:**
- CompaniesPage.tsx → pages/CompaniesPage + features/company/*
- FundDetail.tsx → pages/FundDetailPage + features/fund/*
- EntityList.tsx → pages/EntitiesPage + features/entity/*

**Process for Each Page:**
```
1. Create pages/{Name}/ directory
2. Create features/{domain}/ directory
3. Extract tabs into feature components
4. Move tab logic into features (data fetching, state)
5. Update page to orchestrate features
6. Test each feature independently
7. Test page integration
8. Update routes
9. Delete old files
```

#### Phase 4: Cleanup (1-2 days)
**Goal:** Remove all old code, organize UI components

**Tasks:**
```
1. Delete all *old.ts hook files
2. Delete old component files
3. Move forms/ to ui/Form/
4. Organize ui/ components into subdirectories
5. Update all imports
6. Run linter
7. Run all tests
8. Update documentation
```

### Migration Tracking

Create a tracking document:

```markdown
## Component Migration Tracker

### Phase 1: Forms (Target: Jan 15-18)
- [ ] CreateFundForm (forms/CreateFundModal.tsx → features/fund/CreateFundForm/)
- [ ] CreateCompanyForm (CreateCompanyModal.tsx → features/company/CreateCompanyForm/)
- [ ] CreateEntityForm (CreateEntityModal.tsx → features/entity/CreateEntityForm/)
- [ ] CreateFundEventForm (fund/events/CreateFundEventModal.tsx → features/fund/CreateFundEventForm/)
- [ ] NavUpdateForm (fund/events/create/NavUpdateForm.tsx → part of CreateFundEventForm)
- [ ] DistributionForm (fund/events/create/DistributionForm.tsx → part of CreateFundEventForm)
- [ ] UnitTransactionForm (fund/events/create/UnitTransactionForm.tsx → part of CreateFundEventForm)
- [ ] TaxStatementForm (fund/events/create/TaxStatementForm.tsx → part of CreateFundEventForm)

### Phase 2: Lists (Target: Jan 19-21)
- [ ] FundsTab → CompanyFundsList
- [ ] CompanyList (companies/company-list/) → features/company/CompanyList/
- [ ] EntityList (entities/EntityList.tsx) → features/entity/EntityList/

### Phase 3: Pages (Target: Jan 22-26)
- [ ] CompaniesPage (485 lines → 150 lines + 5 features)
  - [ ] Create pages/CompaniesPage/
  - [ ] Extract overview-tab/ → features/company/CompanyOverview/
  - [ ] Extract funds-tab/ → features/company/CompanyFundsList/ (done in Phase 2)
  - [ ] Extract activity-tab/ → features/company/CompanyActivity/
  - [ ] Extract analysis-tab/ → features/company/CompanyAnalysis/
  - [ ] Extract company-details-tab/ → features/company/CompanyDetails/
  
- [ ] FundDetailPage (447 lines → 120 lines + 2 features)
  - [ ] Create pages/FundDetailPage/
  - [ ] Extract detail/summary/ → features/fund/FundSummary/
  - [ ] Extract detail/table/ → features/fund/FundEventsList/
  
- [ ] EntitiesPage
  - [ ] Create pages/EntitiesPage/
  - [ ] Use features/entity/EntityList/ (done in Phase 2)

### Phase 4: Cleanup (Target: Jan 27-28)
- [ ] Delete old hooks (fundsold/, formsold/, sharedold/, *old.ts)
- [ ] Move forms/ to ui/Form/
- [ ] Organize ui/ components
- [ ] Update all imports
- [ ] Run quality checks
```

---

## Implementation Phases

### Phase 1: Forms Migration (Days 1-4)

#### Day 1: Setup + CreateFundForm
**Morning:**
- Create feature directory structure
- Set up test infrastructure

**Afternoon:**
- Migrate CreateFundModal to CreateFundForm
- Update all imports
- Test thoroughly

**Deliverable:** Working CreateFundForm

#### Day 2: Company & Entity Forms
**Morning:**
- Migrate CreateCompanyModal to CreateCompanyForm

**Afternoon:**
- Migrate CreateEntityModal to CreateEntityForm

**Deliverable:** All entity creation forms migrated

#### Day 3: Fund Event Form (Part 1)
**Morning:**
- Create CreateFundEventForm structure
- Integrate EventTypeSelector

**Afternoon:**
- Migrate NavUpdateForm fields
- Migrate DistributionForm fields

**Deliverable:** 50% of fund event form

#### Day 4: Fund Event Form (Part 2) + Testing
**Morning:**
- Migrate UnitTransactionForm fields
- Migrate TaxStatementForm fields

**Afternoon:**
- Integration testing
- Fix any issues
- Update documentation

**Deliverable:** Complete form migration

---

### Phase 2: Lists Migration (Days 5-7)

#### Day 5: FundsTab → CompanyFundsList
**Morning:**
- Create CompanyFundsList feature
- Remove old UI hooks

**Afternoon:**
- Implement proper data fetching
- Update filters/sorting logic
- Test thoroughly

**Deliverable:** Working CompanyFundsList

#### Day 6: CompanyList
**Morning:**
- Create CompanyList feature
- Extract components

**Afternoon:**
- Update data fetching
- Test functionality

**Deliverable:** Working CompanyList

#### Day 7: EntityList + Testing
**Morning:**
- Create EntityList feature
- Migrate logic

**Afternoon:**
- Integration testing
- Fix any issues
- Update documentation

**Deliverable:** Complete lists migration

---

### Phase 3: Pages Migration (Days 8-12)

#### Day 8: CompaniesPage Setup
**Morning:**
- Create pages/CompaniesPage/
- Extract page component structure

**Afternoon:**
- Set up tab navigation
- Test basic structure

**Deliverable:** Page shell

#### Day 9: CompaniesPage - Overview & Details
**Morning:**
- Extract CompanyOverview feature
- Move data fetching

**Afternoon:**
- Extract CompanyDetails feature
- Test both features

**Deliverable:** 2/5 tabs migrated

#### Day 10: CompaniesPage - Activity & Analysis
**Morning:**
- Extract CompanyActivity feature

**Afternoon:**
- Extract CompanyAnalysis feature
- Test features
- Integration testing

**Deliverable:** Complete CompaniesPage

#### Day 11: FundDetailPage
**Morning:**
- Create pages/FundDetailPage/
- Extract FundSummary feature

**Afternoon:**
- Extract FundEventsList feature
- Test both features

**Deliverable:** Complete FundDetailPage

#### Day 12: EntitiesPage + Testing
**Morning:**
- Create pages/EntitiesPage/
- Integrate EntityList feature

**Afternoon:**
- Integration testing across all pages
- Fix any issues

**Deliverable:** Complete pages migration

---

### Phase 4: Cleanup (Days 13-14)

#### Day 13: Delete Old Code
**Morning:**
- Delete all *old.ts files
- Delete old component directories
- Update imports across codebase

**Afternoon:**
- Verify no broken imports
- Run linter
- Fix any issues

**Deliverable:** Clean codebase

#### Day 14: Final Organization + Documentation
**Morning:**
- Move forms/ to ui/Form/
- Organize ui/ components into subdirectories
- Update all imports

**Afternoon:**
- Run full test suite
- Update documentation
- Create migration guide

**Deliverable:** Production-ready refactor

---

## Testing Strategy

**Note:** Testing strategy and comprehensive test coverage will be addressed in a separate phase after the component refactor is complete. This allows us to:
- Focus migration efforts on architecture and functionality first
- Establish testing patterns once component structure is stable
- Avoid rewriting tests multiple times during refactor

Testing will be covered in a dedicated testing specification that includes:
- Unit testing patterns for presentational components
- Integration testing for feature components with refactored hooks
- E2E testing for complete user workflows
- Testing utilities and helpers for the new architecture

---

## Success Criteria

### Quantitative Metrics

#### Code Quality
```
Before:
- Average page component: 350 lines
- Max component size: 485 lines (CompaniesPage)
- Average useState per page: 8+
- Components using old hooks: 12+

After (Target):
- Average page component: 150 lines (✅ 57% reduction)
- Max component size: 250 lines (✅ 48% reduction)
- Average useState per page: 3-4 (✅ 50% reduction)
- Components using old hooks: 0 (✅ 100% migration)
```

#### Component Metrics
```
Before:
- Total components: 79 files
- Average component size: 200 lines
- Monolithic components: 8
- Reusable UI components: 14

After (Target):
- Total components: ~85 files (✅ slight increase)
- Average component size: 120 lines (✅ 40% reduction)
- Monolithic components: 0 (✅ all split)
- Reusable UI components: 25+ (✅ 78% increase)
```

### Qualitative Metrics

#### Code Maintainability
```
✅ Clear separation of concerns (Pages → Features → UI)
✅ Easy to find code (logical domain-based organization)
✅ Easy to reuse (presentational components)
✅ Consistent patterns (all forms similar, all lists similar)
✅ Type-safe with explicit interfaces and type imports
```

#### Developer Experience
```
✅ Clear where to add new features
✅ Fast to create new components (patterns established)
✅ Easy to onboard new developers (clear structure)
✅ Reduced cognitive load (smaller, focused files)
✅ Better IDE performance (smaller files, better type inference)
✅ Integration with refactored hooks system
```

#### User Experience
```
✅ Consistent behavior (standardized patterns)
✅ Better error handling (centralized error handler)
✅ Better form validation (Zod schemas + transformers)
✅ Reliable data management (refactored hooks)
```

### Acceptance Criteria

#### Must Have (Blocking)
```
✅ All old hooks removed (*old.ts files deleted)
✅ All forms use new form system (schemas + transformers)
✅ All pages split into pages + features
✅ No component over 300 lines
✅ All imports updated (absolute paths, type imports)
✅ TypeScript compilation passes (npx tsc --noEmit)
✅ Linter passes (no errors or warnings)
✅ Proper TypeScript conventions (explicit types, no any, type imports)
```

#### Should Have (High Priority)
```
✅ Component documentation (JSDoc comments)
✅ Migration guide documented
✅ New component templates created
✅ Error handling integrated (useErrorHandler)
✅ Zustand state migration (to URL/local where appropriate)
```

#### Nice to Have (Deferred)
```
⏸️ Comprehensive test coverage (separate phase)
⏸️ Performance optimization (React.memo, useMemo, etc.)
⏸️ Storybook examples for UI components
⏸️ Component visual regression tests
⏸️ Performance benchmarks automated
```

---

## Appendices

### Appendix A: File Migration Map

Complete mapping of old → new file locations:

```
OLD → NEW

# Pages
companies/CompaniesPage.tsx → pages/CompaniesPage/CompaniesPage.tsx
fund/detail/FundDetail.tsx → pages/FundDetailPage/FundDetailPage.tsx
entities/EntityList.tsx → pages/EntitiesPage/EntitiesPage.tsx
OverallDashboard.tsx → pages/DashboardPage/DashboardPage.tsx

# Company Features
companies/overview-tab/OverviewTab.tsx → features/company/CompanyOverview/CompanyOverview.tsx
companies/funds-tab/FundsTab.tsx → features/company/CompanyFundsList/CompanyFundsList.tsx
companies/activity-tab/ActivityTab.tsx → features/company/CompanyActivity/CompanyActivity.tsx
companies/analysis-tab/AnalysisTab.tsx → features/company/CompanyAnalysis/CompanyAnalysis.tsx
companies/company-details-tab/CompanyDetailsTab.tsx → features/company/CompanyDetails/CompanyDetails.tsx
companies/company-list/ → features/company/CompanyList/
companies/create-fund/CreateFundModal.tsx → features/fund/CreateFundForm/CreateFundForm.tsx
CreateCompanyModal.tsx → features/company/CreateCompanyForm/CreateCompanyForm.tsx

# Fund Features
fund/detail/summary/ → features/fund/FundSummary/components/
fund/detail/table/ → features/fund/FundEventsList/components/
fund/events/CreateFundEventModal.tsx → features/fund/CreateFundEventForm/CreateFundEventForm.tsx
fund/events/create/ → features/fund/CreateFundEventForm/components/

# Entity Features
entities/ → features/entity/EntityList/
CreateEntityModal.tsx → features/entity/CreateEntityForm/CreateEntityForm.tsx

# UI Components (Move to subdirectories)
forms/ → ui/Form/
ui/FormField.tsx → ui/Form/FormField.tsx
ui/LoadingSpinner.tsx → ui/Feedback/LoadingSpinner.tsx
ui/ErrorDisplay.tsx → ui/Feedback/ErrorDisplay.tsx
ui/ErrorBoundary.tsx → ui/Feedback/ErrorBoundary.tsx
ui/SuccessBanner.tsx → ui/Feedback/SuccessBanner.tsx
ui/ConfirmDialog.tsx → ui/Modal/ConfirmDialog.tsx
ui/StatusChip.tsx → ui/Chips/StatusChip.tsx
ui/TrackingTypeChip.tsx → ui/Chips/TrackingTypeChip.tsx
ui/EventTypeChip.tsx → ui/Chips/EventTypeChip.tsx
companies/TabNavigation.tsx → ui/Navigation/TabNavigation.tsx

# Layout (Keep)
layout/RouteLayout.tsx → layout/RouteLayout.tsx ✅
layout/MainSidebar.tsx → layout/MainSidebar.tsx ✅
layout/TopBar.tsx → layout/TopBar.tsx ✅

# Delete
fundsold/ → ❌ DELETE
formsold/ → ❌ DELETE
sharedold/ → ❌ DELETE
*old.ts files → ❌ DELETE
```

### Appendix B: Import Path Updates

Update imports across the codebase:

```typescript
// OLD
import { CompaniesPage } from '@/components/companies/CompaniesPage';
import { CreateFundModal } from '@/components/companies/create-fund/CreateFundModal';
import { FundsTab } from '@/components/companies/funds-tab/FundsTab';

// NEW
import { CompaniesPage } from '@/components/pages/CompaniesPage';
import { CreateFundForm } from '@/components/features/fund/CreateFundForm';
import { CompanyFundsList } from '@/components/features/company/CompanyFundsList';
```

### Appendix C: Component Templates

**Page Component Template:**
```typescript
// pages/{Name}/{Name}.tsx
import React, { useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';

export const {Name}Page = () => {
  const { id } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Minimal data fetching
  const { data, loading } = use{Name}(id);
  
  if (loading) return <LoadingSpinner />;
  if (!data) return <ErrorDisplay />;
  
  return (
    <PageLayout>
      {/* Content */}
    </PageLayout>
  );
};
```

**Feature Component Template:**
```typescript
// features/{domain}/{Name}/{Name}.tsx
import React, { useState } from 'react';

export const {Name} = ({ id }: Props) => {
  // Data fetching
  const { data, loading, error, refetch } = use{Name}Data(id);
  
  // Local state
  const [filters, setFilters] = useState({});
  
  // Mutations
  const { mutate } = use{Name}Mutation();
  
  // Event handlers
  const handleAction = () => {
    // Logic
  };
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} />;
  
  return (
    <Box>
      {/* Compose UI components */}
    </Box>
  );
};
```

**UI Component Template:**
```typescript
// ui/{Category}/{Name}/{Name}.tsx
import React from 'react';

interface {Name}Props {
  data: DataType;
  onAction: (item: DataType) => void;
}

export const {Name} = ({ data, onAction }: {Name}Props) => {
  // Only UI-only state allowed
  const [expanded, setExpanded] = useState(false);
  
  return (
    <Box>
      {/* Pure rendering */}
    </Box>
  );
};
```

### Appendix D: Common Pitfalls

**❌ Pitfall 1: Feature Component Doing Too Little**
```typescript
// BAD: Just wrapping data hook
const CompanyOverview = ({ companyId }) => {
  const { data } = useCompanyOverview(companyId);
  return <CompanyOverviewUI data={data} />;
};

// GOOD: Handling state, actions, error
const CompanyOverview = ({ companyId }) => {
  const { data, loading, error, refetch } = useCompanyOverview(companyId);
  const [filters, setFilters] = useState({});
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} onRetry={refetch} />;
  
  return <CompanyOverviewUI data={data} filters={filters} />;
};
```

**❌ Pitfall 2: Page Component Doing Too Much**
```typescript
// BAD: Page fetching all data
const CompaniesPage = () => {
  const { data: overview } = useCompanyOverview(companyId);
  const { data: funds } = useCompanyFunds(companyId);
  const { data: details } = useCompanyDetails(companyId);
  // ... lots of logic
};

// GOOD: Delegate to features
const CompaniesPage = () => {
  const { data: company } = useCompany(companyId); // Just metadata
  
  return (
    <>
      <CompanyOverview companyId={companyId} />  {/* Fetches own data */}
      <CompanyFundsList companyId={companyId} /> {/* Fetches own data */}
    </>
  );
};
```

**❌ Pitfall 3: UI Component Fetching Data**
```typescript
// BAD: UI component fetching data
const FundsTable = ({ companyId }) => {
  const { data } = useFunds({ company_id: companyId });
  return <Table data={data} />;
};

// GOOD: UI component receives data
const FundsTable = ({ funds, onDelete }) => {
  return <Table data={funds} onAction={onDelete} />;
};
```

---

## Conclusion

This specification provides a comprehensive roadmap for refactoring the component architecture to be maintainable, scalable, and enterprise-grade. The phased approach ensures minimal disruption while delivering immediate value through form updates and progressive improvement through list and page refactoring.

**Next Steps:**
1. Review and approve this specification
2. Set up tracking document
3. Begin Phase 1: Forms Migration
4. Track progress daily
5. Adjust timeline as needed

---

**Document Status:** Ready for Review  
**Last Updated:** 2025-01-12  
**Next Review:** After Phase 1 Completion

