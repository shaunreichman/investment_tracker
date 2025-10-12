# Hooks Structure Redesign Specification

## Overview
Redesign and standardize the frontend hooks architecture to create a scalable, maintainable, and consistent structure that supports the recently refactored backend integration while maintaining all existing functionality.

The current hooks directory has mixed concerns with domain-specific data hooks, UI utilities, and infrastructure scattered without clear organization. This redesign establishes a clear categorical structure that separates core infrastructure, data fetching, forms management, UI state, and generic utilities.

## Design Philosophy

### Core Principles
- **Separation of Concerns**: Core infrastructure, domain data, forms, UI state, and utilities each have dedicated directories
- **Single Responsibility**: Each hook has one clear purpose and responsibility
- **Discoverability**: Developers can intuitively find hooks based on category and purpose
- **Composability**: Hooks can be combined to create more complex functionality
- **Type Safety**: Full TypeScript support with proper interfaces and generics
- **Scalability**: Easy to add new domains, UI features, or utilities without restructuring

### Problems We're Solving
- Inconsistent hook organization making it difficult to locate functionality
- Mixed concerns within single hooks (data fetching + UI logic)
- No clear pattern for where new hooks should be created
- Duplicate logic across similar hooks (sorting, filtering)
- Difficult to understand dependencies between hooks
- Lack of standardization for API calls and error handling
- Hard to test hooks due to tight coupling

## Structure

**Note**: This specification focuses on the `hooks/` directory structure. Form-related UI components will be organized in `components/forms/` to complement the hooks architecture with reusable form field components (FormField, FormSelect, FormDatePicker, etc.).

hooks/
├── core/                    # Core infrastructure hooks (rarely change)
│   ├── api/
│   │   ├── useQuery.ts           # Base query hook (GET operations)
│   │   ├── useMutation.ts        # Base mutation hook (POST/PUT/DELETE)
│   │   └── index.ts
│   ├── error/
│   │   ├── useErrorHandler.ts
│   │   ├── useErrorBoundary.ts
│   │   └── index.ts
│   └── index.ts
│
├── data/                    # Domain-specific data fetching hooks
│   ├── funds/
│   │   ├── useFunds.ts
│   │   ├── useFund.ts
│   │   ├── useFundEvents.ts
│   │   ├── useFundFinancialYears.ts
│   │   ├── useFundMutations.ts   # Create/Update/Delete funds
│   │   └── index.ts
│   ├── companies/
│   │   ├── useCompanies.ts
│   │   ├── useCompany.ts
│   │   ├── useCompanyFunds.ts
│   │   ├── useCompanyMutations.ts
│   │   └── index.ts
│   ├── entities/
│   │   ├── useEntities.ts
│   │   ├── useEntity.ts
│   │   ├── useEntityMutations.ts
│   │   └── index.ts
│   ├── banking/
│   │   └── ... (when needed)
│   └── index.ts
│
├── forms/                   # Form management (React Hook Form + Zod)
│   ├── useForm.ts                # Wrapper around React Hook Form
│   ├── types.ts                  # Form types and field configurations
│   ├── schemas/                  # Zod validation schemas
│   │   ├── fundSchemas.ts        # Fund-related schemas
│   │   ├── eventSchemas.ts       # Fund event schemas
│   │   ├── companySchemas.ts     # Company/contact schemas
│   │   ├── entitySchemas.ts      # Entity schemas
│   │   ├── bankingSchemas.ts     # Banking schemas
│   │   ├── rateSchemas.ts     # Banking schemas
│   │   ├── commonSchemas.ts      # Reusable field schemas
│   │   └── index.ts
│   └── index.ts
│
├── ui/                      # UI state and interaction hooks
│   ├── tables/
│   │   ├── useTableSort.ts
│   │   ├── useTableFilters.ts
│   │   ├── useTableSelection.ts
│   │   └── index.ts
│   ├── layout/
│   │   ├── useResponsive.ts
│   │   ├── useBreakpoint.ts
│   │   ├── useSidebar.ts
│   │   └── index.ts
│   ├── search/
│   │   ├── useDebouncedSearch.ts
│   │   ├── useSearchHistory.ts
│   │   └── index.ts
│   ├── modals/
│   │   ├── useModal.ts
│   │   ├── useConfirmDialog.ts
│   │   └── index.ts
│   └── index.ts
│
├── utils/                   # Generic utility hooks
│   ├── useDebounce.ts
│   ├── useThrottle.ts
│   ├── useLocalStorage.ts
│   ├── useMediaQuery.ts
│   ├── usePrevious.ts
│   ├── useInterval.ts
│   ├── useTimeout.ts
│   └── index.ts
│
└── index.ts                 # Main barrel export

## Implementation Strategy

### Phase 1: Core Infrastructure Foundation
**Goal**: Establish foundational hooks that all other hooks will build upon, providing consistent patterns for API calls, error handling, and data fetching.

**Design Principles**:
- Core hooks must be generic and domain-agnostic
- All data fetching should flow through standardized base hooks
- Error handling must be centralized and consistent
- Hooks should support common patterns: loading states, refetch, caching, window focus refetch
- Follow React Query/SWR patterns for familiarity

**Tasks**:
- [x] Create `hooks/core/` directory structure
- [x] Create `hooks/core/api/` subdirectory for API-related hooks
- [x] Implement `useQuery.ts` - base hook for GET operations with loading/error states
- [x] Implement `useMutation.ts` - base hook for POST/PUT/DELETE operations
- [x] Create `hooks/core/error/` subdirectory
- [x] Move `useErrorHandler.ts` to `core/error/`
- [x] Create barrel exports for core hooks (`core/api/index.ts`, `core/error/index.ts`, `core/index.ts`)
- [x] Document core hook APIs with JSDoc comments

**Success Criteria**:
- All core hooks have comprehensive TypeScript interfaces
- Core hooks are completely domain-agnostic (no business logic)
- Loading and error states handled consistently across all core hooks
- Zero dependencies on domain-specific code
- All core hooks have JSDoc documentation
- TypeScript compilation passes with no errors

### Phase 2: Data Layer Organization
**Goal**: Create organized, domain-specific hooks for all backend entities (Funds, Companies, Entities, Banking) that use the core infrastructure hooks.

**Design Principles**:
- One subdirectory per domain entity
- Separate hooks for list queries (plural names) vs single item queries (singular names)
- Group all mutations for a domain in a single mutations file
- Each domain hook should use core `useQuery` or `useMutation` hooks
- Domain transformations and business logic happen in this layer only
- Follow RESTful naming patterns (useFunds, useFund, useFundMutations)

**Tasks**:
- [x] Create `hooks/data/` directory structure
- [x] Create `hooks/data/funds/` subdirectory
- [x] Create `useFunds.ts` with fund queries and mutations (1:1 API mapping)
- [x] Create `useFundEvents.ts` with all event type queries and mutations
- [x] Create `useFundEventCashFlows.ts` with cash flow operations
- [x] Create `useFundTaxStatements.ts` with tax statement operations
- [x] Migrate `useFundFinancialYears.ts` to data/funds/ with path aliases
- [x] Create `hooks/data/companies/` subdirectory
- [x] Create `useCompanies.ts` with company queries and mutations
- [x] Create `useContacts.ts` with contact operations
- [x] Create `hooks/data/entities/` subdirectory
- [x] Create `useEntities.ts` with entity queries and mutations
- [x] Create `hooks/data/banking/` subdirectory
- [x] Create `useBanks.ts` with bank queries and mutations
- [x] Create `useBankAccounts.ts` with bank account operations
- [x] Create `useBankAccountBalances.ts` with balance operations
- [x] Create barrel exports for each domain
- [x] Create main data barrel export (`data/index.ts`)

**Success Criteria**:
- All domain hooks use core infrastructure hooks (no direct fetch calls)
- Clear separation between read operations (queries) and write operations (mutations)
- Each domain has consistent naming patterns
- Domain-specific transformations are properly typed
- All data hooks work with refactored backend endpoints
- Zero business logic in core hooks, all in data layer
- Barrel exports allow clean imports from domain directories

### Phase 3: Forms Management Layer
**Goal**: Implement enterprise-grade form management using React Hook Form + Zod for type-safe, performant, and consistent form handling across the application.

**Design Principles**:
- **Enterprise Best Practice**: Use React Hook Form (state management) + Zod (schema validation)
- **Type Safety**: Full TypeScript inference from Zod schemas
- **Performance**: Uncontrolled components minimize re-renders
- **Consistency**: Thin wrapper layer provides application-specific patterns
- **Standardization**: All forms follow the same schema-based validation approach
- **DX**: Leverage battle-tested libraries instead of custom solutions
- **Material-UI Integration**: Seamless integration with existing MUI components

**Why React Hook Form + Zod**:
- Battle-tested with millions of downloads
- Minimal re-renders (uncontrolled components)
- Excellent TypeScript inference from schemas
- Feature-complete: field arrays, nested objects, dynamic forms, async validation
- React Hook Form DevTools for debugging
- Small bundle size (~9kb, tree-shakeable)
- Industry-standard solution

**Implementation Patterns**:

#### Field Configuration Pattern
Forms use a **schema-first approach** where the Zod schema is the single source of truth:

```typescript
// Schema defines validation (type-safe, composable)
const fundSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters").max(255),
  managementFee: z.number().positive("Fee must be positive").max(100, "Fee cannot exceed 100%"),
  currency: z.enum(['USD', 'EUR', 'GBP']),
  foundedDate: z.date().optional()
});

type FundFormData = z.infer<typeof fundSchema>; // Auto-generated TypeScript type

// Optional: UI metadata separate from validation
const fundFieldConfig: FormFieldsConfig<FundFormData> = {
  name: { label: 'Fund Name', helpText: 'Enter a unique name for this fund' },
  managementFee: { label: 'Management Fee (%)', helpText: 'Annual management fee percentage' },
  currency: { label: 'Base Currency' },
  foundedDate: { label: 'Founded Date', helpText: 'Optional founding date' }
};
```

**Key Principles**:
- ✅ One schema per form (enables field relationship validation)
- ✅ Schema generates TypeScript types via `z.infer`
- ✅ UI metadata (labels, help text) separated from validation logic
- ✅ Validation errors defined in schema (e.g., `.min(2, "error message")`)
- ❌ Do NOT create per-field schemas (breaks composition and relationships)

#### Validation Display Rules
**Consistent rules across ALL forms to ensure uniform UX:**

**1. Required Field Indicators:**
- Red asterisk (*) displayed next to label when field is required
- Asterisk ALWAYS visible (regardless of error state)
- Implementation: Check if field is required in schema (e.g., not `.optional()`)

**2. Field Error States:**
- **Red outline on input**: Show when `fieldState.error` exists AND field is `touched`
- **Error message below field**: Show when `fieldState.error` exists AND field is `touched`
- **Helper text**: Show when NO error OR field not yet touched
- **Error takes precedence**: If both error and helperText exist, show error only

**3. Validation Timing:**
- **Default: onBlur** - Validate when user leaves field (better UX, less intrusive)
- **onChange**: Only for real-time validation needs (passwords, username availability)
- **onSubmit**: Always validate ALL fields on submit attempt
- **Configurable**: Allow per-form override via `mode` prop in useForm wrapper

**4. Error Message Priority:**
- First: Zod schema validation errors (type, range, pattern, custom messages)
- Second: Custom cross-field validation errors (via `.refine()` or `.superRefine()`)
- Third: API/server errors (after form submission)

**5. Visual Implementation with Material-UI:**
```typescript
<TextField
  {...field}
  error={!!fieldState.error && fieldState.isTouched}  // Red outline
  helperText={
    fieldState.isTouched && fieldState.error
      ? fieldState.error.message  // Show error if touched
      : fieldConfig.helpText      // Show help text otherwise
  }
  label={
    <span>
      {fieldConfig.label}
      {isRequired && <span style={{ color: 'red' }}> *</span>}
    </span>
  }
/>
```

#### Integration with Existing Components

**1. NumberInputField Integration:**
Preserve existing formatting behavior while integrating with React Hook Form:
```typescript
// Wrap existing NumberInputField with Controller
<Controller
  name="managementFee"
  control={form.control}
  render={({ field, fieldState }) => (
    <NumberInputField
      {...field}
      label="Management Fee"
      allowDecimals={true}
      allowNegative={false}
      error={!!fieldState.error && fieldState.isTouched}
      helperText={
        fieldState.isTouched && fieldState.error
          ? fieldState.error.message
          : "Annual management fee percentage"
      }
      // Preserve existing formatting behavior
      onInputChange={(name, value) => field.onChange(value)}
    />
  )}
/>
```
- ✅ Keep thousand separator formatting
- ✅ Keep focus/blur clean/format behavior
- ✅ Map to React Hook Form's field API
- ✅ Maintain existing NumberInputField component

**2. FormField Component Enhancement:**
Enhance (don't replace) existing FormField component:
- Already has: required indicator, error display, helper text structure
- Add: Proper touched state handling for conditional error display
- Add: Integration with React Hook Form's fieldState
- Keep: Existing visual styling and layout

**3. FormContainer Integration:**
FormContainer already accepts `isValid`, `isDirty`, `isSubmitting` - perfect for RHF:
```typescript
<FormContainer
  open={open}
  title="Create Fund"
  onClose={onClose}
  onSubmit={form.handleSubmit}
  isSubmitting={form.formState.isSubmitting}
  isValid={form.formState.isValid}
  isDirty={form.formState.isDirty}
>
  {/* Form fields */}
</FormContainer>
```
- ✅ No changes needed to FormContainer
- ✅ React Hook Form provides all required props
- ✅ Existing modal behavior preserved

#### Form Patterns

**1. Conditional Fields:**
Fields that appear/disappear based on other field values (e.g., DistributionForm):
```typescript
// Watch field value to show/hide other fields
const distributionType = form.watch('distributionType');
const subType = form.watch('subDistributionType');

// Conditional rendering
{distributionType === 'INTEREST' && subType === 'WITHHOLDING_TAX' && (
  <>
    <Controller name="grossAmount" control={form.control} render={...} />
    <Controller name="withholdingTaxAmount" control={form.control} render={...} />
  </>
)}

// Conditional validation in schema
const distributionSchema = z.object({
  distributionType: z.enum(['INTEREST', 'DIVIDEND', 'OTHER']),
  subDistributionType: z.string().optional(),
  amount: z.number().positive().optional(),
  grossAmount: z.number().positive().optional(),
  withholdingTaxAmount: z.number().min(0).optional(),
}).refine((data) => {
  // If INTEREST with WITHHOLDING_TAX, grossAmount is required
  if (data.distributionType === 'INTEREST' && data.subDistributionType === 'WITHHOLDING_TAX') {
    return data.grossAmount !== undefined;
  }
  return true;
}, {
  message: "Gross amount is required for interest with withholding tax",
  path: ["grossAmount"]
});
```

**2. Field Arrays (Dynamic Lists):**
For forms with repeating sections (e.g., multiple cash flows):
```typescript
const { fields, append, remove } = useFieldArray({
  control: form.control,
  name: "cashFlows"
});

// Render dynamic fields
{fields.map((field, index) => (
  <div key={field.id}>
    <Controller
      name={`cashFlows.${index}.amount`}
      control={form.control}
      render={...}
    />
    <Button onClick={() => remove(index)}>Remove</Button>
  </div>
))}
<Button onClick={() => append({ amount: 0, date: '' })}>Add Cash Flow</Button>
```

**3. Date Range Validation:**
Cross-field validation for date ranges:
```typescript
const dateRangeSchema = z.object({
  startDate: z.date(),
  endDate: z.date()
}).refine((data) => data.endDate >= data.startDate, {
  message: "End date must be after start date",
  path: ["endDate"]
});
```

**4. Dependent Dropdowns:**
When one field's options depend on another:
```typescript
const fundType = form.watch('fundType');
const availableStrategies = getStrategiesForFundType(fundType);

<Controller
  name="strategy"
  control={form.control}
  render={({ field }) => (
    <Select {...field}>
      {availableStrategies.map(s => <MenuItem value={s.id}>{s.name}</MenuItem>)}
    </Select>
  )}
/>
```

#### Migration Example: Before & After

**Before (NavUpdateForm - Manual State Management):**
```typescript
interface NavUpdateFormProps {
  formData: {
    event_date?: string;
    nav_per_share?: string;
    description?: string;
  };
  validationErrors: {
    event_date?: string;
    nav_per_share?: string;
    description?: string;
  };
  onInputChange: (field: string, value: string) => void;
}

const NavUpdateForm: React.FC<NavUpdateFormProps> = ({
  formData,
  validationErrors,
  onInputChange,
}) => {
  return (
    <Box>
      <TextField
        label={<span>Event Date <span style={{color: 'red'}}>*</span></span>}
        type="date"
        value={formData.event_date || ''}
        onChange={(e) => onInputChange('event_date', e.target.value)}
        fullWidth
        error={!!validationErrors.event_date}
        helperText={validationErrors.event_date}
        InputLabelProps={{ shrink: true }}
      />
      
      <NumberInputField
        label={<span>NAV per Share <span style={{color: 'red'}}>*</span></span>}
        value={formData.nav_per_share || ''}
        onInputChange={onInputChange}
        fieldName="nav_per_share"
        allowDecimals={true}
        allowNegative={false}
        fullWidth
        error={!!validationErrors.nav_per_share}
        helperText={validationErrors.nav_per_share}
      />
      
      <TextField
        label="Description (Optional)"
        value={formData.description || ''}
        onChange={(e) => onInputChange('description', e.target.value)}
        fullWidth
        error={!!validationErrors.description}
        helperText={validationErrors.description}
      />
    </Box>
  );
};
```

**After (NavUpdateForm - React Hook Form + Zod):**
```typescript
import { z } from 'zod';
import { useForm } from '@/hooks/forms';
import { Controller } from 'react-hook-form';

// Schema with validation
const navUpdateSchema = z.object({
  event_date: z.string().min(1, 'Event date is required'),
  nav_per_share: z.number()
    .positive('NAV per share must be positive')
    .finite('NAV per share must be a valid number'),
  description: z.string().optional()
});

type NavUpdateFormData = z.infer<typeof navUpdateSchema>;

// Field configurations
const navFieldConfig = {
  event_date: { label: 'Event Date', helpText: 'Date of NAV update' },
  nav_per_share: { label: 'NAV per Share', helpText: 'Net Asset Value per share' },
  description: { label: 'Description', helpText: 'Optional notes about this NAV update' }
};

interface NavUpdateFormProps {
  fundId: string;
  onSuccess: () => void;
  onCancel: () => void;
}

const NavUpdateForm: React.FC<NavUpdateFormProps> = ({
  fundId,
  onSuccess,
  onCancel
}) => {
  const { mutate: createNavUpdate } = useFundEventMutations();
  
  const form = useForm<NavUpdateFormData>({
    schema: navUpdateSchema,
    fieldConfig: navFieldConfig,
    defaultValues: {
      event_date: '',
      nav_per_share: 0,
      description: ''
    },
    onSubmit: async (data) => {
      await createNavUpdate({
        fundId,
        eventType: 'NAV_UPDATE',
        ...data
      });
      onSuccess();
    }
  });

  return (
    <FormContainer
      open={true}
      title="NAV Update"
      onClose={onCancel}
      onSubmit={form.handleSubmit}
      isSubmitting={form.formState.isSubmitting}
      isValid={form.formState.isValid}
      isDirty={form.formState.isDirty}
    >
      <Box display="grid" gridTemplateColumns="1fr" gap={2}>
        {/* Date Field */}
        <Controller
          name="event_date"
          control={form.control}
          render={({ field, fieldState }) => (
            <TextField
              {...field}
              type="date"
              label={
                <span>
                  {form.getFieldConfig('event_date').label}
                  <span style={{color: 'red'}}> *</span>
                </span>
              }
              error={!!fieldState.error && fieldState.isTouched}
              helperText={
                fieldState.isTouched && fieldState.error
                  ? fieldState.error.message
                  : form.getFieldConfig('event_date').helpText
              }
              InputLabelProps={{ shrink: true }}
              fullWidth
            />
          )}
        />
        
        {/* Number Field with existing NumberInputField */}
        <Controller
          name="nav_per_share"
          control={form.control}
          render={({ field, fieldState }) => (
            <NumberInputField
              {...field}
              label={
                <span>
                  {form.getFieldConfig('nav_per_share').label}
                  <span style={{color: 'red'}}> *</span>
                </span>
              }
              allowDecimals={true}
              allowNegative={false}
              error={!!fieldState.error && fieldState.isTouched}
              helperText={
                fieldState.isTouched && fieldState.error
                  ? fieldState.error.message
                  : form.getFieldConfig('nav_per_share').helpText
              }
              onInputChange={(name, value) => field.onChange(value)}
              fullWidth
            />
          )}
        />
        
        {/* Optional Text Field */}
        <Controller
          name="description"
          control={form.control}
          render={({ field, fieldState }) => (
            <TextField
              {...field}
              label={form.getFieldConfig('description').label}
              error={!!fieldState.error && fieldState.isTouched}
              helperText={
                fieldState.isTouched && fieldState.error
                  ? fieldState.error.message
                  : form.getFieldConfig('description').helpText
              }
              multiline
              rows={3}
              fullWidth
            />
          )}
        />
      </Box>
    </FormContainer>
  );
};
```

**Key Improvements:**
- ❌ **Before**: 3 props (formData, validationErrors, onInputChange), manual state management
- ✅ **After**: 3 props (fundId, onSuccess, onCancel), all form state handled by RHF
- ❌ **Before**: No type safety on form data
- ✅ **After**: Full TypeScript inference from Zod schema
- ❌ **Before**: Manual validation logic scattered in parent component
- ✅ **After**: Validation centralized in schema
- ❌ **Before**: Red outline shows on ANY error (even before user interaction)
- ✅ **After**: Red outline only shows when touched AND error
- ❌ **Before**: Error message always shows if exists
- ✅ **After**: Error message only shows when touched, otherwise shows helpText
- ✅ **After**: Directly integrates with mutation hook (no parent state)

**Tasks**:
- [x] Install dependencies: `react-hook-form`, `@hookform/resolvers`, `zod`
- [x] Create `hooks/forms/` directory structure
- [x] Create `hooks/forms/types.ts` - shared form types and field configuration interfaces
- [x] Create `hooks/forms/useForm.ts` - wrapper around React Hook Form with app-specific patterns
- [x] Create `hooks/forms/schemas/` subdirectory for reusable Zod schemas
- [x] Create common field schemas (currency, percentage, date, email, etc.)
- [x] Create `components/forms/` directory for reusable form components
- [x] Create `FormTextField.tsx` - standardized text field component with error/label/helpText
- [x] Create `FormSelectField.tsx` - select field component with RHF Controller
- [x] Create `FormDateField.tsx` - date field component with RHF Controller
- [x] Create `FormNumberField.tsx` - number field with formatting (integrates with existing NumberInputField)
- [x] Create form schemas for each domain:
  - [x] `schemas/fundSchemas.ts` - Fund creation/update schemas (aligned with backend)
  - [x] `schemas/fundEventSchemas.ts` - Fund event schemas (NAV, distributions, transactions, tax statements, cost-based)
  - [x] `schemas/companySchemas.ts` - Company and contact schemas (aligned with backend)
  - [x] `schemas/entitySchemas.ts` - Entity schemas (aligned with backend)
  - [x] `schemas/bankingSchemas.ts` - Bank, account, and balance schemas (aligned with backend)
  - [x] `schemas/rateSchemas.ts` - FX and risk-free rate schemas (aligned with backend)
- [x] Create barrel exports (`forms/index.ts`, `forms/schemas/index.ts`)
- [x] Document form patterns with examples in JSDoc (comprehensive comments in all files)
- [ ] Create field configurations for common form patterns
- [ ] Migrate existing forms to new pattern:
  - [ ] NavUpdateForm
  - [ ] DistributionForm
  - [ ] TaxStatementForm
  - [ ] UnitTransactionForm
  - [ ] CostBasedEventForm
  - [ ] Fund creation/edit forms
  - [ ] Company forms
  - [ ] Entity forms
- [ ] Evaluate and refactor `useEventSubmission.ts` - integrate with RHF approach
- [ ] Create form usage documentation with examples

**Success Criteria**:

**Validation & Display:**
- ✅ All forms use React Hook Form + Zod validation
- ✅ Schema validation provides full TypeScript type inference via `z.infer<typeof schema>`
- ✅ Red outline appears ONLY when field has error AND is touched
- ✅ Error message displays below field ONLY when field has error AND is touched
- ✅ Helper text displays when field has NO error OR not yet touched
- ✅ Required fields show red asterisk (*) at ALL times (not just on error)
- ✅ All forms use onBlur validation by default (configurable per form)
- ✅ All fields validate on submit attempt (mark all as touched)

**Schema & Type Safety:**
- ✅ One Zod schema per form (no per-field schemas)
- ✅ Schema enables cross-field validation (date ranges, conditional required fields)
- ✅ TypeScript types auto-generated from schemas via `z.infer`
- ✅ Validation error messages defined in schema (e.g., `.min(2, "error message")`)
- ✅ Reusable common schemas for currency, percentage, dates, email
- ✅ Schema composition for complex forms (e.g., `.refine()` for conditional validation)

**Component Integration:**
- ✅ NumberInputField wrapped with Controller, formatting preserved
- ✅ FormField component enhanced for touched state handling
- ✅ FormContainer works unchanged (receives isValid, isDirty, isSubmitting from RHF)
- ✅ Material-UI components integrated via Controller
- ✅ Existing component behavior preserved (no visual regressions)

**Form Patterns:**
- ✅ Conditional fields implemented using `watch()` and conditional rendering
- ✅ Conditional validation implemented using `.refine()` or `.superRefine()`
- ✅ Field arrays supported via `useFieldArray` for dynamic lists
- ✅ Date range validation works via schema `.refine()`
- ✅ Dependent dropdowns work via `watch()` for reactive options

**Code Quality:**
- ✅ Zero custom form state management code (all handled by RHF)
- ✅ Form performance optimized (minimal re-renders via uncontrolled components)
- ✅ Form submission integrates with existing mutation hooks from data layer
- ✅ TypeScript compilation passes with zero errors
- ✅ All migrated forms pass existing tests (no breaking changes)
- ✅ Consistent patterns across all forms (copy-paste-able code)

**Documentation:**
- ✅ Field configuration pattern documented with examples
- ✅ Validation display rules documented with visual examples
- ✅ Integration patterns documented for each existing component
- ✅ Common form patterns documented (conditional fields, arrays, ranges)
- ✅ Migration examples showing before/after for at least one form

### Phase 4: UI State & Interaction Layer
**Goal**: Organize all UI state management hooks by feature category (tables, layout, search, modals) with no data fetching concerns.

**Design Principles**:
- UI hooks manage only client-side state (no API calls)
- Organized by UI feature/component type for easy discovery
- Hooks should be composable (can use multiple UI hooks together)
- Generic and reusable across different data types
- Support responsive design patterns
- No domain-specific logic (works with any data)

**Tasks**:
- [ ] Create `hooks/ui/` directory structure
- [ ] Create `hooks/ui/tables/` subdirectory
- [ ] Move and rename `useTableSorting.ts` to `ui/tables/useTableSort.ts`
- [ ] Generalize and move `useFundsFilters.ts` to `ui/tables/useTableFilters.ts`
- [ ] Create `useTableSelection.ts` for row selection state
- [ ] Create `hooks/ui/layout/` subdirectory
- [ ] Move and rename `useResponsiveView.ts` to `ui/layout/useResponsive.ts`
- [ ] Create `useBreakpoint.ts` for current breakpoint detection
- [ ] Create `useSidebar.ts` for sidebar toggle state
- [ ] Create `hooks/ui/search/` subdirectory
- [ ] Move `useDebouncedSearch.ts` to `ui/search/`
- [ ] Create `useSearchHistory.ts` for recent searches
- [ ] Create `hooks/ui/modals/` subdirectory
- [ ] Create `useModal.ts` for modal open/close state
- [ ] Create `useConfirmDialog.ts` for confirmation dialogs
- [ ] Create barrel exports for each UI category
- [ ] Create main UI barrel export (`ui/index.ts`)

**Success Criteria**:
- All UI hooks are pure (no API calls or data fetching)
- UI hooks work with any data type through generics
- Table hooks can be composed together for full table functionality
- Layout hooks support responsive design patterns
- Clear separation between UI state and data state
- All UI hooks fully typed with TypeScript interfaces
- Barrel exports enable organized imports by feature

### Phase 5: Utilities & Migration
**Goal**: Extract generic utility hooks and complete migration from old structure to new structure with full backward compatibility during transition.

**Design Principles**:
- Utility hooks must be framework-agnostic patterns (could be npm package)
- Zero business logic in utilities
- Each utility hook solves one specific technical problem
- Utilities should be tested in isolation
- Maintain backward compatibility through barrel exports during migration
- Remove old hook files only after all imports updated

**Tasks**:
- [ ] Create `hooks/utils/` directory
- [ ] Create `useDebounce.ts` - debounce any value
- [ ] Create `useThrottle.ts` - throttle callbacks
- [ ] Create `useLocalStorage.ts` - sync state with localStorage
- [ ] Create `useMediaQuery.ts` - match media queries
- [ ] Create `usePrevious.ts` - track previous state value
- [ ] Create `useInterval.ts` - setInterval with cleanup
- [ ] Create `useTimeout.ts` - setTimeout with cleanup
- [ ] Create utility barrel export (`utils/index.ts`)
- [ ] Create main hooks barrel export (`hooks/index.ts`) that re-exports all categories
- [ ] Add deprecation comments to old hook locations
- [ ] Update all component imports to use new hook locations
- [ ] Update barrel exports to maintain backward compatibility
- [ ] Run full test suite to verify no breaking changes
- [ ] Update import paths across codebase systematically (by domain)
- [ ] Remove old hook files after all imports migrated
- [ ] Remove old directory structure (`hooks/shared/`, `hooks/funds/`, etc.)
- [ ] Update documentation and examples with new import patterns

**Success Criteria**:
- All utility hooks are generic and reusable in any React project
- Main barrel export provides single entry point for all hooks
- Zero breaking changes to existing components during migration
- All imports updated to new structure
- Old files and directories removed
- Full test coverage maintained throughout migration
- TypeScript compilation passes with zero errors
- No console warnings about deprecated imports
- Documentation reflects new structure with clear examples

## Overall Success Metrics

### Organizational Metrics
- All hooks organized into 5 clear categories: core, data, forms, ui, utils
- Each category has subdirectories grouping related functionality
- Barrel exports at every level enable clean imports
- Developers can find hooks within 10 seconds based on category

### Code Quality Metrics
- 100% TypeScript compilation success with no errors or warnings
- All hooks have proper TypeScript interfaces and generics
- All public hooks have JSDoc documentation
- Zero console errors or warnings in development
- ESLint passes with no errors

### Functional Metrics
- All existing functionality preserved (zero breaking changes to UI)
- All components using hooks continue to work without modification during migration
- Backend integration works correctly with all refactored endpoints
- Loading states, error handling, and data fetching consistent across all hooks
- Form validation and submission working for all forms

### Developer Experience Metrics
- New developers can locate appropriate hooks within first viewing
- Hook imports follow consistent, predictable patterns
- Clear examples in documentation for each hook category
- Easy to add new hooks without restructuring
- Composability allows complex functionality from simple hooks

### Performance Metrics
- No performance degradation from restructuring
- Efficient re-renders (hooks don't cause unnecessary updates)
- Proper cleanup on unmount for all hooks
- Memory leaks eliminated through proper dependency management

