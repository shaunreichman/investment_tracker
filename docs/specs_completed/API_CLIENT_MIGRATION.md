# API Client Migration Guide

**Created**: 2025-10-08  
**Purpose**: Document the migration from monolithic API client to domain-organized structure  
**Status**: Phase 1 - Banking migrated, other domains pending

---

## 📁 New Structure

```
services/
├── api-client.ts              // Base ApiClient class (200 lines)
│   └── Handles: request(), get(), post(), put(), delete()
│
├── api/                       // Domain-specific APIs
│   ├── banking.api.ts         // ✅ Banking API (150 lines)
│   ├── fund.api.ts            // ⏳ TODO: Migrate from api.ts
│   ├── company.api.ts         // ⏳ TODO: Migrate from api.ts
│   ├── entity.api.ts          // ⏳ TODO: Migrate from api.ts
│   ├── rates.api.ts           // ⏳ TODO: Create new
│   └── index.ts               // Unified export
│
└── api.ts                     // Legacy (will be removed)
```

---

## 🎯 New Usage Pattern

### **Before (Old Monolithic)**:
```typescript
import { apiClient } from '../services/api';

// Unclear what domain this belongs to
const response = await apiClient.getBanks();
const bank = await apiClient.createBank(data);
```

### **After (Domain-Organized)**:
```typescript
import { api } from '@/services/api';

// Clear domain separation
const response = await api.banking.getBanks();
const bank = await api.banking.createBank(data);

// Future domains
const funds = await api.funds.getFunds();
const entities = await api.entities.getEntities();
```

---

## ✅ Benefits Achieved

### 1. **Clear Domain Separation**
- Banking methods in `banking.api.ts`
- Funds methods in `fund.api.ts` (when migrated)
- No confusion about where methods belong

### 2. **Smaller, Focused Files**
- **Before**: 800+ lines in one file
- **After**: 150-200 lines per domain
- Easier to navigate and maintain

### 3. **Type Safety**
```typescript
// Full type safety with domain models
import { api } from '@/services/api';
import { Bank, CreateBankRequest } from '@/types/models/banking';

const data: CreateBankRequest = {
  name: 'Test Bank',
  country: Country.US,
  bank_type: BankType.COMMERCIAL
};

const bank: Bank = await api.banking.createBank(data);
```

### 4. **Parallel Development**
Multiple developers can work on different domains without conflicts:
- Developer A: `banking.api.ts`
- Developer B: `fund.api.ts`
- No merge conflicts!

### 5. **Tree-Shaking Ready**
```typescript
// Only import what you need
import { BankingApi } from '@/services/api';

// Or use unified interface
import { api } from '@/services/api';
```

---

## 🔄 Migration Status

### ✅ Completed
- [x] Base ApiClient extracted to `api-client.ts`
- [x] Banking API migrated to `api/banking.api.ts`
- [x] Unified export created in `api/index.ts`
- [x] Legacy api.ts marked for deprecation

### ⏳ Pending Migration
- [ ] Funds API → `api/fund.api.ts`
- [ ] Companies API → `api/company.api.ts`
- [ ] Entities API → `api/entity.api.ts`
- [ ] Rates API → `api/rates.api.ts`

### 🗑️ Cleanup (After Full Migration)
- [ ] Remove banking methods from legacy api.ts
- [ ] Eventually delete api.ts entirely
- [ ] Update all component imports

---

## 📝 How to Use

### **Import the unified API**:
```typescript
import { api } from '@/services/api';
```

### **Banking Operations**:
```typescript
// Get all banks
const { banks, count } = await api.banking.getBanks({
  country: Country.US,
  include_bank_accounts: true
});

// Get single bank
const { bank } = await api.banking.getBank(1, {
  include_bank_accounts: true
});

// Create bank
const newBank = await api.banking.createBank({
  name: 'Chase Bank',
  country: Country.US,
  bank_type: BankType.COMMERCIAL,
  swift_bic: 'CHASUS33'
});

// Update bank
const updated = await api.banking.updateBank(1, {
  name: 'JPMorgan Chase'
});

// Delete bank
await api.banking.deleteBank(1);
```

### **Bank Accounts**:
```typescript
// Get all bank accounts for an entity
const { bank_accounts } = await api.banking.getBankAccounts({
  entity_id: 5,
  include_bank: true,
  include_entity: true
});

// Create bank account
const account = await api.banking.createBankAccount({
  entity_id: 5,
  bank_id: 1,
  account_name: 'Main Operating Account',
  account_number: '1234567890',
  currency: Currency.USD,
  account_type: BankAccountType.CHECKING
});
```

### **Error Handling**:
```typescript
import { ApiError } from '@/services/api';

try {
  const bank = await api.banking.createBank(data);
} catch (error) {
  if (error instanceof ApiError) {
    // Structured error handling
    console.error('Status:', error.status);
    console.error('Code:', error.responseCode);
    console.error('User message:', error.userFriendlyMessage);
    
    if (error.isClientError) {
      // Handle 4xx errors
    } else if (error.isServerError) {
      // Handle 5xx errors
    }
  }
}
```

---

## 🚀 Adding New Domain APIs

When creating a new domain API (e.g., Rates):

### 1. **Create the API class**:
```typescript
// services/api/rates.api.ts
import { ApiClient } from '../api-client';
import { RiskFreeRate, CreateRateRequest } from '../../types/models/rates';

export class RatesApi {
  constructor(private client: ApiClient) {}
  
  async getRates(params?) {
    return this.client.get('/api/risk-free-rates', params);
  }
  
  async createRate(data: CreateRateRequest) {
    return this.client.post('/api/risk-free-rates', data);
  }
}
```

### 2. **Add to unified export**:
```typescript
// services/api/index.ts
import { RatesApi } from './rates.api';

const rates = new RatesApi(apiClient);

export const api = {
  banking,
  rates,  // Add new domain
  // ...
};
```

### 3. **Use in components**:
```typescript
import { api } from '@/services/api';

const rates = await api.rates.getRates();
```

---

## 🔍 Advanced Usage

### **Direct API Client Access**:
```typescript
import { apiClient } from '@/services/api';

// For custom requests not in domain APIs
const response = await apiClient.request('/api/custom-endpoint');
```

### **Custom API Instance**:
```typescript
import { ApiClient } from '@/services/api';

// Create custom client (e.g., for different base URL)
const customClient = new ApiClient('https://api.other-service.com');
```

### **Type-Safe API Interface**:
```typescript
import { Api } from '@/services/api';

// Use in React Context or custom hooks
const ApiContext = createContext<Api | null>(null);

// In component
const api = useContext(ApiContext);
const banks = await api?.banking.getBanks();
```

---

## 📊 Metrics

### **File Size Reduction**:
- **Before**: 1 file × 800 lines = 800 lines
- **After**: 
  - Base client: 200 lines
  - Banking API: 150 lines
  - Unified export: 50 lines
  - **Total**: 400 lines (50% reduction with better organization)

### **Estimated Full Migration**:
- Base client: 200 lines
- Banking API: 150 lines
- Funds API: 200 lines
- Companies API: 150 lines
- Entities API: 50 lines
- Rates API: 100 lines
- Unified export: 50 lines
- **Total**: ~900 lines (vs. 2000+ in monolithic)

---

## 🎯 Migration Checklist

When migrating a domain from `api.ts` to its own file:

- [ ] Create `services/api/{domain}.api.ts`
- [ ] Import types from `types/models/{domain}.ts`
- [ ] Move all methods from `api.ts` to new file
- [ ] Update method signatures to use proper types
- [ ] Add to unified export in `services/api/index.ts`
- [ ] Test all methods work correctly
- [ ] Update component imports (if any use old format)
- [ ] Remove methods from legacy `api.ts`

---

## 📚 Related Documentation

- **Type Definitions**: `types/models/` - Domain model interfaces
- **Enum Definitions**: `types/enums/` - Domain enum definitions
- **DTO Definitions**: `types/dto/` - API response/request DTOs
- **Backend Routes**: `src/api/routes/` - Backend endpoint definitions

---

**Remember**: Always use the unified `api` object from `services/api/index.ts` for consistency!
