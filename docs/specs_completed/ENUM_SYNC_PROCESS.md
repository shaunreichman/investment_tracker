# Enum Synchronization Process

**Created**: 2025-10-08  
**Purpose**: Document the process for keeping frontend TypeScript enums synchronized with backend Python enums  
**Criticality**: HIGH - Enum mismatches cause API communication failures

---

## Overview

The investment tracker system uses enums extensively for type-safe API communication. Backend Python enums and frontend TypeScript enums **must remain identical** for the system to function correctly. This document defines the synchronization process.

---

## 🎯 Core Principle

**Backend is the single source of truth for all enum definitions.**

The Python backend enums define the canonical values. TypeScript enums are derived copies that must match exactly.

---

## 📁 File Structure

### Backend Enum Locations
```
src/
├── fund/enums/
│   ├── fund_enums.py
│   ├── fund_event_enums.py
│   ├── fund_event_cash_flow_enums.py
│   └── fund_tax_statement_enums.py
├── entity/enums/
│   └── entity_enums.py
├── banking/enums/
│   ├── bank_enums.py
│   ├── bank_account_enums.py
│   └── bank_account_balance_enums.py
├── company/enums/
│   ├── company_enums.py
│   └── company_contact_enums.py
├── rates/enums/
│   ├── fx_rate_enums.py
│   └── risk_free_rate_enums.py
└── shared/enums/
    ├── shared_enums.py
    └── domain_update_event_enums.py
```

### Frontend Enum Locations
```
frontend/src/types/enums/
├── fund.enums.ts
├── entity.enums.ts
├── banking.enums.ts
├── company.enums.ts
├── rates.enums.ts
├── shared.enums.ts
└── index.ts (barrel export)
```

---

## 🔄 When to Sync Enums

### 1. Backend Enum is Created
**Trigger**: New Python enum is added to any domain  
**Action**: Create corresponding TypeScript enum immediately

### 2. Backend Enum is Modified
**Trigger**: Values added, removed, or renamed in Python enum  
**Action**: Update TypeScript enum to match within same PR/commit

### 3. Backend Enum is Deleted
**Trigger**: Python enum is removed  
**Action**: Remove TypeScript enum and update all references

---

## 📝 Manual Sync Process (Current)

### Step 1: Identify Changes
When working on backend:
```bash
# Check for enum changes in your branch
git diff main -- "src/**/enums/*.py"
```

### Step 2: Update TypeScript Enums
For each changed Python enum:

1. **Open the corresponding TypeScript enum file**
   - Fund enums → `frontend/src/types/enums/fund.enums.ts`
   - Entity enums → `frontend/src/types/enums/entity.enums.ts`
   - Banking enums → `frontend/src/types/enums/banking.enums.ts`
   - Company enums → `frontend/src/types/enums/company.enums.ts`
   - Rates enums → `frontend/src/types/enums/rates.enums.ts`
   - Shared enums → `frontend/src/types/enums/shared.enums.ts`

2. **Copy the enum values exactly**
   ```python
   # Backend: src/fund/enums/fund_enums.py
   class FundStatus(Enum):
       ACTIVE = 'ACTIVE'
       SUSPENDED = 'SUSPENDED'
       REALIZED = 'REALIZED'
       COMPLETED = 'COMPLETED'
   ```
   
   ```typescript
   // Frontend: frontend/src/types/enums/fund.enums.ts
   export enum FundStatus {
     ACTIVE = 'ACTIVE',
     SUSPENDED = 'SUSPENDED',
     REALIZED = 'REALIZED',
     COMPLETED = 'COMPLETED'
   }
   ```

3. **Preserve TypeScript-specific features**
   - Keep JSDoc comments
   - Maintain helper functions (type guards)
   - Keep enum descriptions and documentation

### Step 3: Update Barrel Export (if new enum)
If adding a new enum, export it from `frontend/src/types/enums/index.ts`

### Step 4: Test Synchronization
Run integration test to verify enums match:
```bash
cd frontend
npm test -- enum.sync.test
```

---

## ✅ Validation Checklist

Before considering enum sync complete:

- [ ] **Exact Value Match**: Every backend enum value exists in TypeScript
- [ ] **No Extra Values**: TypeScript has no values that backend doesn't have
- [ ] **Correct Casing**: All values use exact same casing (usually UPPER_CASE)
- [ ] **Documentation Updated**: TypeScript enum has JSDoc comments explaining usage
- [ ] **Helper Functions**: Type guard functions match backend class methods (if applicable)
- [ ] **Barrel Export**: New enum is exported from `index.ts`
- [ ] **Audit Document**: `BACKEND_ENUM_AUDIT.md` is updated to reflect changes

---

## 🚨 Special Cases

### CompanyType Enum
**WARNING**: This enum uses human-readable strings, NOT UPPER_CASE

```python
# Backend: USES TITLE CASE WITH SPACES
class CompanyType(Enum):
    PRIVATE_EQUITY = 'Private Equity'  # NOT 'PRIVATE_EQUITY'
    VENTURE_CAPITAL = 'Venture Capital'
```

```typescript
// Frontend: MUST MATCH EXACTLY
export enum CompanyType {
  PRIVATE_EQUITY = 'Private Equity',  // Same format!
  VENTURE_CAPITAL = 'Venture Capital'
}
```

### Helper Functions
Some backend enums have class methods that should be replicated as TypeScript functions:

```python
# Backend: src/fund/enums/fund_event_enums.py
@classmethod
def is_equity_event(cls, event_type: 'EventType') -> bool:
    return event_type in {cls.CAPITAL_CALL, cls.RETURN_OF_CAPITAL}
```

```typescript
// Frontend: frontend/src/types/enums/fund.enums.ts
export function isEquityEvent(eventType: EventType): boolean {
  return [
    EventType.CAPITAL_CALL,
    EventType.RETURN_OF_CAPITAL
  ].includes(eventType);
}
```

---

## 🧪 Testing Strategy

### Integration Test Template
Create `frontend/src/types/enums/__tests__/enum.sync.test.ts`:

```typescript
/**
 * Enum Synchronization Tests
 * 
 * These tests verify that frontend enums match backend enums.
 * If these tests fail, update the TypeScript enums to match Python enums.
 */

describe('Enum Synchronization', () => {
  describe('FundStatus', () => {
    it('should have all backend values', async () => {
      // Call backend endpoint that returns enum values
      const backendValues = await apiClient.getEnumValues('FundStatus');
      const frontendValues = Object.values(FundStatus);
      
      expect(frontendValues.sort()).toEqual(backendValues.sort());
    });
  });

  // Repeat for each enum...
});
```

### Backend Helper Endpoint (Optional)
Create an endpoint that returns all enum values for testing:

```python
@health_check_bp.route('/api/enums/<enum_name>', methods=['GET'])
def get_enum_values(enum_name: str):
    """Return all values for a given enum (for testing sync)."""
    enum_map = {
        'FundStatus': [e.value for e in FundStatus],
        'EventType': [e.value for e in EventType],
        # ... all enums
    }
    return jsonify({'values': enum_map.get(enum_name, [])})
```

---

## 🔮 Future Automation

### Phase 1: Manual Process (Current)
✅ **Status**: Implemented  
- Manual copying of enum values
- Human review and validation
- Integration tests catch drift

### Phase 2: OpenAPI Code Generation (Future)
🎯 **Goal**: Automate TypeScript enum generation from backend

**Implementation**:
1. Generate OpenAPI spec from Flask routes
2. Use `openapi-typescript` to generate TypeScript types
3. CI/CD pipeline regenerates types on backend changes

**Tools**:
- `flask-smorest` or `flasgger` for OpenAPI generation
- `openapi-typescript` for TypeScript generation
- GitHub Actions for automation

**Benefits**:
- Zero human error
- Automatic synchronization
- Single source of truth enforced

### Phase 3: Schema-First Development (Future)
🎯 **Goal**: Define enums in neutral format, generate both Python and TypeScript

**Implementation**:
- Define enums in JSON Schema or Protocol Buffers
- Generate both Python and TypeScript from schema
- Schema becomes the source of truth

---

## 📚 Developer Workflow

### When Adding a New Enum

1. **Backend Developer**:
   ```bash
   # 1. Create Python enum
   vim src/domain/enums/new_enum.py
   
   # 2. Update __init__.py to export it
   vim src/domain/enums/__init__.py
   
   # 3. Notify in PR description: "Added NewEnum - needs frontend sync"
   git commit -m "feat(domain): add NewEnum"
   ```

2. **Frontend Developer** (or same developer):
   ```bash
   # 1. Create TypeScript enum
   vim frontend/src/types/enums/domain.enums.ts
   
   # 2. Export from barrel file
   vim frontend/src/types/enums/index.ts
   
   # 3. Update audit document
   vim docs/specs_completed/BACKEND_ENUM_AUDIT.md
   
   git commit -m "feat(frontend): sync NewEnum from backend"
   ```

### When Modifying an Enum

1. **Backend Change**:
   ```bash
   # Modify Python enum
   vim src/domain/enums/existing_enum.py
   git commit -m "feat(domain): add NEW_VALUE to ExistingEnum"
   ```

2. **Frontend Sync** (same PR):
   ```bash
   # Update TypeScript enum
   vim frontend/src/types/enums/domain.enums.ts
   git add frontend/src/types/enums/domain.enums.ts
   git commit --amend --no-edit
   ```

---

## 🔍 Troubleshooting

### Problem: TypeScript Compilation Error
```
Error: Type 'string' is not assignable to type 'FundStatus'
```

**Solution**: Check if frontend enum is missing values that backend has

### Problem: API Returns Unknown Enum Value
```
console.error: Received unknown FundStatus: 'NEW_STATUS'
```

**Solution**: Backend added a new enum value, update TypeScript enum

### Problem: Tests Failing After Backend Update
```
Expected: ['ACTIVE', 'SUSPENDED']
Received: ['ACTIVE', 'SUSPENDED', 'REALIZED']
```

**Solution**: Backend enum was updated, sync to frontend

---

## 📊 Maintenance

### Monthly Review
- Review `BACKEND_ENUM_AUDIT.md` for accuracy
- Check for enum drift using integration tests
- Update this document with lessons learned

### Quarterly Planning
- Evaluate automation opportunities
- Consider OpenAPI migration
- Review enum usage patterns

---

## 🤝 Collaboration Guidelines

### Backend-Frontend Coordination
- **Always mention enum changes in PR descriptions**
- **Tag frontend team on enum changes**
- **Don't merge backend enum changes without frontend sync**
- **Use conventional commit messages**: `feat(enums): add/modify/remove EnumName`

### Code Review
When reviewing PRs with enum changes:
- [ ] Verify TypeScript enum matches Python enum exactly
- [ ] Check that barrel export is updated
- [ ] Confirm documentation is updated
- [ ] Validate integration tests pass

---

## 📖 References

- **Backend Enum Audit**: `docs/specs_completed/BACKEND_ENUM_AUDIT.md`
- **Integration Spec**: `docs/specs_completed/FRONTEND_BACKEND_INTEGRATION.md`
- **Backend Enums**: `src/**/enums/*.py`
- **Frontend Enums**: `frontend/src/types/enums/*.ts`

---

**Remember**: Enum mismatches are **runtime errors** that only appear in production. Always sync enums in the same PR as backend changes.
