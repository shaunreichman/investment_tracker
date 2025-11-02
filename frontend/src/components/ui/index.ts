// ============================================================================
// UI COMPONENTS - BARREL EXPORT (LEGACY)
// ============================================================================
//
// STILL IN USE (needs migration):
//   - FormField: Used in CreateCompanyModal, CreateEntityModal
//   - FormSection: Pattern replaced, but check for usage
//
// MIGRATION PLAN:
//   1. Migrate CreateCompanyModal to RHF + shared/forms
//   2. Migrate CreateEntityModal to RHF + shared/forms
//   3. Delete this directory
//
// ============================================================================

// ⚠️ DEPRECATED - Temporary exports for legacy components
export { FormField } from './FormField';
export type { FormFieldProps } from './FormField';