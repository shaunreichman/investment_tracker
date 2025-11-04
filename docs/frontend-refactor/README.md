# Frontend Refactor Specifications

This folder contains all specifications for the frontend refactor from flat component structure to domain-driven architecture.

## Specifications

- **[00-MASTER.md](00-MASTER.md)** - Master specification with overview, dependencies, and coordination
- **[00-FILE_STRUCTURE.md](00-FILE_STRUCTURE.md)** - Complete detailed file structure with all nested folders and components

## Phase Specifications

1. **[01-SHARED_DOMAIN.md](01-SHARED_DOMAIN.md)** - Phase 1: Shared Domain Structure
2. **[02-COMPANY_DOMAIN.md](02-COMPANY_DOMAIN.md)** - Phase 2: Company Domain
3. **[03-FUND_DOMAIN.md](03-FUND_DOMAIN.md)** - Phase 3: Fund Domain
4. **[04-SUPPORTING_DOMAINS.md](04-SUPPORTING_DOMAINS.md)** - Phase 4: Supporting Domains (Banking, Entity, Rates)
5. **[05-ROUTING_CLEANUP.md](05-ROUTING_CLEANUP.md)** - Phases 5 & 6: Routing & Cleanup

## Execution Order

See [00-MASTER.md](00-MASTER.md) for complete dependency graph and execution order.

```
Phase 1: Shared Domain (Foundation)
    ↓
Phases 2, 3, 4: Domain Migrations (Can be parallel after Phase 1)
    ├─→ Phase 2: Company Domain
    ├─→ Phase 3: Fund Domain
    └─→ Phase 4: Supporting Domains
    ↓
Phases 5 & 6: Routing & Cleanup (After all domains complete)
```

