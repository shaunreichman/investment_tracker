// ============================================================================
// HOOKS INDEX
// ============================================================================

// Core hooks (API, error handling)
export * from './core';

// Data hooks (domain-specific API calls)
export * from './data';

// Form hooks (validation, schemas, transformers)
export * from './forms';

// UI hooks (generic UI state management)
export * from './ui';

// ============================================================================
// OLD HOOKS (TO BE REMOVED)
// ============================================================================

export { useApiCall } from './useApiCallold';
export { useEntities } from './useEntitiesold';
export { useEventSubmission } from './useEventSubmissionold';
export { useFunds } from './useFundsold';
export { useFundFinancialYears } from './useFundFinancialYearsold';
export { useCompanies } from './useCompaniesold';
export { useNumberInput } from './useNumberInputold';

// New organized hooks
export * from './sharedold';
export * from './fundsold';
