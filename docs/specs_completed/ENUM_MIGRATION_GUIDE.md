# Enum Migration Guide: types/api.ts → types/enums/

**Created**: 2025-10-08  
**Purpose**: Guide for migrating from old monolithic enum file to new organized structure  
**Status**: Phase 1.1 Complete - Ready for Phase 2 Implementation

---

## Overview

The frontend previously had enums defined in `frontend/src/types/api.ts` alongside interfaces and types. We've now created a proper domain-organized enum structure in `frontend/src/types/enums/` that exactly matches the backend.

This document guides the migration from old to new enums.

---

## 📊 Migration Status

### Old Location
```
frontend/src/types/api.ts
├── FundTrackingType ✅ (correct)
├── FundStatus ✅ (correct)
├── EventType ⚠️ (has extra values not in backend)
├── DistributionType ❌ (wrong values - needs replacement)
├── TaxPaymentType ❌ (wrong values - needs replacement)
├── GroupType ✅ (correct)
├── EntityType ✅ (correct)
└── Country ✅ (correct)
```

### New Location
```
frontend/src/types/enums/
├── fund.enums.ts (13 enums - all correct)
├── entity.enums.ts (2 enums - all correct)
├── banking.enums.ts (7 enums - NEW DOMAIN)
├── company.enums.ts (4 enums - NEW DOMAIN)
├── rates.enums.ts (3 enums - NEW DOMAIN)
├── shared.enums.ts (6 enums - includes Currency, SortOrder, etc.)
└── index.ts (barrel export)
```

---

## 🔄 Migration Strategy

### Phase 1: Coexistence (Current)
- Old enums in `types/api.ts` remain
- New enums in `types/enums/` are available
- Components can use either (temporarily)
- No breaking changes yet

### Phase 2: Gradual Migration (Next)
- Update components one-by-one to use new enums
- Add deprecation comments to old enums
- Run tests after each component migration

### Phase 3: Cleanup (Final)
- Remove old enum definitions from `types/api.ts`
- Ensure all imports point to `types/enums`
- Run full test suite
- Update documentation

---

## 🔧 Step-by-Step Migration

### Step 1: Update Import Statements

#### Before (Old)
```typescript
import { FundStatus, EventType, EntityType } from '../types/api';
```

#### After (New)
```typescript
import { FundStatus, EventType, EntityType } from '@/types/enums';
```

### Step 2: Handle Breaking Changes

#### DistributionType - BREAKING CHANGE

**Old (Incorrect)**:
```typescript
export enum DistributionType {
  INTEREST = 'INTEREST',
  DIVIDEND = 'DIVIDEND',
  OTHER = 'OTHER'
}
```

**New (Correct)**:
```typescript
export enum DistributionType {
  INCOME = 'INCOME',
  DIVIDEND_FRANKED = 'DIVIDEND_FRANKED',
  DIVIDEND_UNFRANKED = 'DIVIDEND_UNFRANKED',
  INTEREST = 'INTEREST',
  RENT = 'RENT',
  CAPITAL_GAIN = 'CAPITAL_GAIN'
}
```

**Migration Action**:
1. Search for all uses of `DistributionType.DIVIDEND`
2. Determine if it should be `DIVIDEND_FRANKED` or `DIVIDEND_UNFRANKED`
3. Update code accordingly
4. Remove `DistributionType.OTHER` references (no longer exists)

```bash
# Find all usages
grep -r "DistributionType\." frontend/src/components/
```

#### TaxPaymentType - BREAKING CHANGE

**Old (Incorrect)**:
```typescript
export enum TaxPaymentType {
  INTEREST_TAX = 'INTEREST_TAX',
  DIVIDEND_TAX = 'DIVIDEND_TAX',
  CAPITAL_GAINS_TAX = 'CAPITAL_GAINS_TAX',
  NON_RESIDENT_INTEREST_WITHHOLDING = 'NON_RESIDENT_INTEREST_WITHHOLDING',
  EOFY_INTEREST_TAX = 'EOFY_INTEREST_TAX',
  DIVIDENDS_FRANKED_TAX = 'DIVIDENDS_FRANKED_TAX',
  DIVIDENDS_UNFRANKED_TAX = 'DIVIDENDS_UNFRANKED_TAX'
}
```

**New (Correct - Backend Values Only)**:
```typescript
export enum TaxPaymentType {
  NON_RESIDENT_INTEREST_WITHHOLDING = 'NON_RESIDENT_INTEREST_WITHHOLDING',
  CAPITAL_GAINS_TAX = 'CAPITAL_GAINS_TAX',
  EOFY_INTEREST_TAX = 'EOFY_INTEREST_TAX',
  DIVIDENDS_FRANKED_TAX = 'DIVIDENDS_FRANKED_TAX',
  DIVIDENDS_UNFRANKED_TAX = 'DIVIDENDS_UNFRANKED_TAX'
}
```

**Migration Action**:
1. `INTEREST_TAX` → map to `EOFY_INTEREST_TAX` or another appropriate value
2. `DIVIDEND_TAX` → map to `DIVIDENDS_FRANKED_TAX` or `DIVIDENDS_UNFRANKED_TAX`
3. Review each usage individually

#### EventType - BREAKING CHANGE

**Old (Has Extra Values)**:
```typescript
export enum EventType {
  // ... standard values ...
  MANAGEMENT_FEE = 'MANAGEMENT_FEE',      // ❌ NOT IN BACKEND
  CARRIED_INTEREST = 'CARRIED_INTEREST',  // ❌ NOT IN BACKEND
  OTHER = 'OTHER'                         // ❌ NOT IN BACKEND
}
```

**New (Backend Only)**:
```typescript
export enum EventType {
  CAPITAL_CALL = 'CAPITAL_CALL',
  RETURN_OF_CAPITAL = 'RETURN_OF_CAPITAL',
  DISTRIBUTION = 'DISTRIBUTION',
  UNIT_PURCHASE = 'UNIT_PURCHASE',
  UNIT_SALE = 'UNIT_SALE',
  NAV_UPDATE = 'NAV_UPDATE',
  DAILY_RISK_FREE_INTEREST_CHARGE = 'DAILY_RISK_FREE_INTEREST_CHARGE',
  EOFY_DEBT_COST = 'EOFY_DEBT_COST',
  TAX_PAYMENT = 'TAX_PAYMENT'
}
```

**Migration Action**:
1. Find all uses of `MANAGEMENT_FEE`, `CARRIED_INTEREST`, `OTHER`
2. Determine if backend supports these (check with backend team)
3. If not supported, remove UI features using these values
4. If needed, request backend to add these enum values

---

## 📝 Component Migration Checklist

For each component using old enums:

- [ ] **Find all enum imports**
  ```bash
  # Search for old import pattern
  grep -l "from.*types/api" frontend/src/components/**/*.tsx
  ```

- [ ] **Update import to new location**
  ```typescript
  // Old
  import { FundStatus } from '../types/api';
  
  // New
  import { FundStatus } from '@/types/enums';
  ```

- [ ] **Check for breaking changes**
  - DistributionType usage?
  - TaxPaymentType usage?
  - EventType.MANAGEMENT_FEE, CARRIED_INTEREST, or OTHER?

- [ ] **Update usage if needed**
  ```typescript
  // Old
  if (dist.type === DistributionType.DIVIDEND) { ... }
  
  // New - need to determine which one
  if (dist.type === DistributionType.DIVIDEND_FRANKED) { ... }
  // OR
  if (dist.type === DistributionType.DIVIDEND_UNFRANKED) { ... }
  ```

- [ ] **Run component tests**
  ```bash
  npm test -- ComponentName.test.tsx
  ```

- [ ] **Check TypeScript compilation**
  ```bash
  npx tsc --noEmit
  ```

---

## 🎯 Migration Priority Order

### High Priority (Core Functionality)
1. **Fund Components**
   - `FundDetail.tsx`
   - `FundDetailTable/*`
   - `CreateFundEventModal.tsx`
   - Event form components

2. **Entity Components**
   - `CreateEntityModal.tsx`
   - Any entity selection dropdowns

### Medium Priority (Company Features)
3. **Company Components**
   - `CompaniesPage.tsx`
   - `CreateCompanyModal.tsx`
   - Company detail tabs

### Low Priority (Utility Components)
4. **Shared Components**
   - `EventTypeChip.tsx`
   - `StatusChip.tsx`
   - Filter components

---

## 🧪 Testing Strategy

### 1. Unit Tests
For each migrated component:
```typescript
import { FundStatus } from '@/types/enums';

describe('ComponentName', () => {
  it('should use correct enum values', () => {
    // Test that component works with new enum
    expect(Object.values(FundStatus)).toContain('ACTIVE');
  });
});
```

### 2. Integration Tests
Test API communication:
```typescript
it('should send correct enum values to API', async () => {
  const response = await apiClient.createFund({
    status: FundStatus.ACTIVE,
    tracking_type: FundTrackingType.NAV_BASED
  });
  
  expect(response).toBeDefined();
});
```

### 3. E2E Tests
Test full user workflows with new enums

---

## 🚨 Common Migration Issues

### Issue 1: Type Errors After Migration
```typescript
// Error: Type 'DIVIDEND' does not exist on type 'DistributionType'
const type = DistributionType.DIVIDEND;
```

**Solution**: Use new enum values
```typescript
const type = DistributionType.DIVIDEND_FRANKED;
// or
const type = DistributionType.DIVIDEND_UNFRANKED;
```

### Issue 2: API Returns Unknown Enum Value
```typescript
// Console: Warning - received unknown value 'RENT' for DistributionType
```

**Solution**: Update TypeScript enum to include all backend values (already done in new enums)

### Issue 3: Component Tests Failing
```typescript
// Error: Expected 'DIVIDEND' to be in enum values
```

**Solution**: Update test expectations to use new enum values

---

## 📦 New Features Available

With the new enum structure, you gain access to:

### 1. Helper Functions
```typescript
import { isEquityEvent, isTaxableDistribution } from '@/types/enums';

// Instead of manual checks
if (event.type === EventType.CAPITAL_CALL || 
    event.type === EventType.RETURN_OF_CAPITAL) {
  // ...
}

// Use helper
if (isEquityEvent(event.type)) {
  // ...
}
```

### 2. Banking Enums (NEW)
```typescript
import { 
  BankType, 
  BankAccountType, 
  BankAccountStatus 
} from '@/types/enums';

// Now available for banking features
```

### 3. Company Enums (NEW)
```typescript
import { CompanyType, CompanyStatus } from '@/types/enums';

// Proper company type handling
```

### 4. Currency Enum (NEW)
```typescript
import { Currency, getCurrencyDecimalPlaces } from '@/types/enums';

// Better currency handling
const decimals = getCurrencyDecimalPlaces(Currency.JPY); // 0
const decimalsUSD = getCurrencyDecimalPlaces(Currency.USD); // 2
```

---

## 🔍 Verification Checklist

After migration complete:

- [ ] **No imports from old location**
  ```bash
  # Should return nothing
  grep -r "from.*types/api.*FundStatus\|EventType\|EntityType" frontend/src/
  ```

- [ ] **All components use new enums**
  ```bash
  # Should show imports from types/enums
  grep -r "from.*types/enums" frontend/src/components/
  ```

- [ ] **TypeScript compiles without errors**
  ```bash
  cd frontend && npx tsc --noEmit
  ```

- [ ] **All tests pass**
  ```bash
  cd frontend && npm test
  ```

- [ ] **No ESLint warnings**
  ```bash
  cd frontend && npm run lint
  ```

---

## 📅 Timeline Recommendation

### Week 1: Preparation
- Review this guide with team
- Identify all components using old enums
- Create migration task list

### Week 2-3: Core Migration
- Migrate fund components
- Migrate entity components
- Run tests continuously

### Week 4: Company & Shared
- Migrate company components
- Migrate utility components
- Handle breaking changes

### Week 5: Cleanup & Validation
- Remove old enum definitions
- Update all documentation
- Final testing pass

---

## 🤝 Team Coordination

### Before Starting Migration
- [ ] Team meeting to discuss breaking changes
- [ ] Agree on DistributionType mapping strategy
- [ ] Decide on EventType extra values (keep or remove)
- [ ] Create feature branch for migration

### During Migration
- [ ] Daily sync on progress
- [ ] Document any unexpected issues
- [ ] Update this guide with learnings

### After Migration
- [ ] Code review all changes
- [ ] Run full regression test suite
- [ ] Update component architecture docs

---

## 📖 References

- **Backend Enum Audit**: `docs/specs_completed/BACKEND_ENUM_AUDIT.md`
- **Enum Sync Process**: `docs/specs_completed/ENUM_SYNC_PROCESS.md`
- **New Enum Files**: `frontend/src/types/enums/*.ts`
- **Old Enum File**: `frontend/src/types/api.ts` (lines 40-110)

---

**Note**: This migration is part of Phase 2 (Domain Integration). Complete Phase 1 tasks first before starting this migration.
